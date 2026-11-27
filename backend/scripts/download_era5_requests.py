"""Download and validate two existing ERA5-Land CDS request results.

This script only retrieves the two fixed object-store URLs below. It never
submits a CDS request and does not use account credentials or browser cookies.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import struct
import time
import urllib.parse
import zipfile
import zlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOWNLOAD_DIR = PROJECT_ROOT / "data" / "raw" / "weather" / "era5_land"
MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "era5_land_download_manifest.json"
DATASET_URL = "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land"
LICENSE_URL = "https://apps.ecmwf.int/datasets/licences/copernicus/"
CDS_TERMS_URL = "https://cds.climate.copernicus.eu/disclaimer-privacy"
ATTRIBUTION = (
    "Generated using Copernicus Climate Change Service information [Year]. "
    "For adapted or modified material: Contains modified Copernicus Climate "
    "Change Service information [Year]. Neither the European Commission nor "
    "ECMWF is responsible for any use that may be made of the information."
)
CHUNK_SIZE = 1024 * 1024
MAX_GRIB_MESSAGE_BYTES = 64 * 1024 * 1024
CONNECT_TIMEOUT_SECONDS = 30
READ_TIMEOUT_SECONDS = 120
MAX_REDIRECTS = 5

REQUESTS = (
    {
        "request_number": 1,
        "request_reference": "24a5f33e75200171321741639baf695f",
        "url": (
            "https://object-store.os-api.cci2.ecmwf.int/"
            "cci2-prod-cache-1/2026-11-19/"
            "24a5f33e75200171321741639baf695f.zip"
        ),
        "filename": "era5_land_request_1.zip",
        "user_reported_approx_size": "2.03 GB",
    },
    {
        "request_number": 2,
        "request_reference": "7aa7a686527d3e900aa7b8dce4709fa6",
        "url": (
            "https://object-store.os-api.cci2.ecmwf.int/"
            "cci2-prod-cache-3/2026-11-19/"
            "7aa7a686527d3e900aa7b8dce4709fa6.zip"
        ),
        "filename": "era5_land_request_2.zip",
        "user_reported_approx_size": "647 MB",
    },
)
ALLOWED_HOST = "object-store.os-api.cci2.ecmwf.int"


class DownloadError(RuntimeError):
    """A safe-to-display download or validation failure."""


def _safe_http_error(status_code: int) -> DownloadError:
    if status_code in {401, 403, 404, 410}:
        return DownloadError(
            "The existing download link returned HTTP %d. It may have expired or "
            "requires authorization. Open the successful request in the official "
            "Copernicus CDS account and obtain a fresh download link; do not provide "
            "credentials or browser cookies to this script." % status_code
        )
    return DownloadError("The official object store returned HTTP %d." % status_code)


def _session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.auth = None
    session.cookies.clear()
    return session


def _request_response(
    session: requests.Session, method: str, url: str, headers: dict[str, str] | None = None
) -> requests.Response:
    current_url = url
    for _ in range(MAX_REDIRECTS + 1):
        parsed = urllib.parse.urlsplit(current_url)
        if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
            raise DownloadError("The request URL is not the official object-store HTTPS host.")
        session.cookies.clear()
        try:
            response = session.request(
                method,
                current_url,
                headers=headers,
                timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS),
                allow_redirects=False,
                stream=True,
            )
        except requests.RequestException:
            raise DownloadError("The official object store request failed or timed out.") from None
        session.cookies.clear()
        if response.status_code in {301, 302, 303, 307, 308}:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise DownloadError("The official object store returned a redirect without a target.")
            current_url = urllib.parse.urljoin(current_url, location)
            continue
        if response.status_code >= 400:
            status_code = response.status_code
            response.close()
            raise _safe_http_error(status_code)
        response_host = urllib.parse.urlsplit(response.url).hostname
        if response_host != ALLOWED_HOST:
            response.close()
            raise DownloadError("The response did not come from the official object store.")
        return response
    raise DownloadError("The official object store exceeded the redirect limit.")


def _content_length(headers: object) -> int | None:
    value = headers.get("Content-Length")  # type: ignore[attr-defined]
    if value is None:
        return None
    try:
        length = int(value)
    except (TypeError, ValueError):
        raise DownloadError("The server returned an invalid Content-Length header.") from None
    if length < 0:
        raise DownloadError("The server returned a negative Content-Length header.")
    return length


def _head(url: str) -> tuple[int | None, bool, str | None]:
    with _session() as session:
        response = _request_response(
            session,
            "HEAD",
            url,
            {"User-Agent": "AgroSense-360-ERA5-Land-downloader/1.0"},
        )
        try:
            if response.status_code != 200:
                raise DownloadError("The official object store HEAD request failed.")
            length = _content_length(response.headers)
            content_type = response.headers.get("Content-Type")
            accepts_ranges = response.headers.get("Accept-Ranges", "").casefold() == "bytes"
            return length, accepts_ranges, content_type
        finally:
            response.close()


def _content_range(value: str | None) -> tuple[int, int, int] | None:
    if value is None:
        return None
    match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", value.strip(), re.IGNORECASE)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def _request_stream(
    session: requests.Session, url: str, offset: int, expected_total: int | None
) -> requests.Response:
    headers = {"User-Agent": "AgroSense-360-ERA5-Land-downloader/1.0"}
    if offset:
        headers["Range"] = "bytes=%d-" % offset
    response = _request_response(session, "GET", url, headers)
    if offset:
        content_range = _content_range(response.headers.get("Content-Range"))
        total = content_range[2] if content_range else None
        if (
            response.status_code != 206
            or content_range is None
            or content_range[0] != offset
            or content_range[1] < offset
            or (total is not None and content_range[1] >= total)
            or (expected_total is not None and total != expected_total)
        ):
            response.close()
            raise DownloadError(
                "The server did not confirm the requested byte range; the partial file "
                "was preserved and has not been appended."
            )
    elif response.status_code != 200:
        response.close()
        raise DownloadError("The download did not return HTTP 200.")

    content_type = response.headers.get("Content-Type", "").casefold()
    if "zip" not in content_type and "octet-stream" not in content_type:
        response.close()
        raise DownloadError("The object store response did not identify a ZIP/binary archive.")
    return response


def _download(
    request: dict[str, object],
    target: Path,
    remote_length: int | None,
    supports_ranges: bool,
) -> int:
    partial = target.with_suffix(target.suffix + ".part")
    if target.exists():
        raise DownloadError("Refusing to overwrite an existing archive: %s" % target.name)

    offset = partial.stat().st_size if partial.exists() else 0
    if offset:
        if not supports_ranges or remote_length is None:
            raise DownloadError(
                "A partial archive exists, but the server did not advertise byte ranges "
                "with a known total length. The partial file was preserved."
            )
        if offset > remote_length:
            raise DownloadError(
                "The partial archive exceeds the server's declared size; "
                "the partial file was preserved."
            )
        if offset == remote_length:
            return offset

    with _session() as session:
        response = _request_stream(session, str(request["url"]), offset, remote_length)
        response_length = _content_length(response.headers)
        expected_body_length = remote_length - offset if remote_length is not None else None
        if (
            response_length is not None
            and expected_body_length is not None
            and response_length != expected_body_length
        ):
            response.close()
            raise DownloadError("The response Content-Length does not match the verified archive size.")

        total_length = remote_length or (
            offset + response_length if response_length is not None else None
        )
        mode = "ab" if partial.exists() else "xb"
        downloaded = offset
        started = time.monotonic()
        try:
            with response, partial.open(mode) as output:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if not chunk:
                        continue
                    output.write(chunk)
                    downloaded += len(chunk)
                    elapsed = max(time.monotonic() - started, 0.001)
                    size_text = "%.2f MiB" % (downloaded / (1024 * 1024))
                    if total_length:
                        percent = min(downloaded * 100.0 / total_length, 100.0)
                        print(
                            "\rRequest %d: %5.1f%%  %s / %.2f MiB  %.2f MiB/s"
                            % (
                                request["request_number"],
                                percent,
                                size_text,
                                total_length / (1024 * 1024),
                                (downloaded - offset) / (1024 * 1024) / elapsed,
                            ),
                            end="",
                            flush=True,
                        )
                    else:
                        print(
                            "\rRequest %d: %s downloaded"
                            % (request["request_number"], size_text),
                            end="",
                            flush=True,
                        )
                output.flush()
                os.fsync(output.fileno())
        except (requests.RequestException, TimeoutError, OSError):
            print()
            raise DownloadError(
                "The download was interrupted. The partial archive was preserved; rerun "
                "to resume only if the server confirms the exact HTTP byte range."
            ) from None
        finally:
            response.close()
    print()

    actual_size = partial.stat().st_size
    if total_length is not None and actual_size != total_length:
        raise DownloadError(
            "Downloaded size does not match the server's Content-Length; "
            "the partial archive was preserved."
        )
    return actual_size


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _zip_inventory(path: Path) -> tuple[list[dict[str, object]], bool]:
    try:
        if not zipfile.is_zipfile(path):
            raise DownloadError("Downloaded archive is not a valid ZIP file.")
        contents: list[dict[str, object]] = []
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                contents.append(
                    {
                        "name": info.filename,
                        "size_bytes": info.file_size,
                        "compressed_size_bytes": info.compress_size,
                        "is_directory": info.is_dir(),
                    }
                )
            bad_member = archive.testzip()
    except (OSError, zipfile.BadZipFile, RuntimeError, zlib.error):
        raise DownloadError(
            "The archive could not be opened or CRC-tested as a valid ZIP file."
        ) from None
    return contents, bad_member is None


def _read_grib_metadata(
    path: Path, contents: list[dict[str, object]]
) -> dict[str, object] | None:
    members = [
        str(item["name"])
        for item in contents
        if Path(str(item["name"])).suffix.casefold() in {".grib", ".grb", ".grb2"}
    ]
    if not members:
        return None

    try:
        import eccodes
    except ImportError:
        raise DownloadError(
            "GRIB files were found but the eccodes metadata reader is unavailable."
        ) from None

    variable_records: dict[tuple[object, ...], dict[str, object]] = {}
    timestamps: set[datetime] = set()
    variable_timestamps: dict[tuple[object, ...], set[datetime]] = {}
    latitudes: list[float] = []
    longitudes: list[float] = []
    grid_types: set[str] = set()
    grid_increments: set[tuple[float, float]] = set()
    earth_shapes: set[str] = set()
    editions: set[int] = set()
    missing_value_markers: set[str] = set()
    missing_count_values: set[int] = set()
    total_value_counts: set[int] = set()
    message_length_mismatches: list[dict[str, object]] = []
    message_count = 0

    def get(handle: object, key: str) -> object | None:
        if not eccodes.codes_is_defined(handle, key):  # type: ignore[arg-type]
            return None
        try:
            return eccodes.codes_get(handle, key)  # type: ignore[arg-type]
        except eccodes.CodesInternalError as error:
            raise DownloadError(
                "ecCodes could not read a metadata key from the GRIB message."
            ) from error

    def read_exact(stream: object, size: int) -> bytes:
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = stream.read(remaining)  # type: ignore[attr-defined]
            if not chunk:
                raise DownloadError("A GRIB message ended before its declared length.")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    with zipfile.ZipFile(path) as archive:
        for member in members:
            member_messages = 0
            member_size = archive.getinfo(member).file_size
            with archive.open(member, "r") as stream:
                while True:
                    prefix = stream.read(4)
                    if not prefix:
                        break
                    if prefix != b"GRIB":
                        if member_messages and not any(prefix):
                            for padding in iter(
                                lambda: stream.read(CHUNK_SIZE), b""
                            ):
                                if any(padding):
                                    raise DownloadError(
                                        "A GRIB archive member has non-padding bytes "
                                        "after its last message."
                                    )
                            break
                        raise DownloadError("A GRIB archive member has an invalid message header.")
                    first_header = read_exact(stream, 4)
                    edition = first_header[3]
                    if edition == 1:
                        message_length = int.from_bytes(first_header[:3], "big")
                        header = prefix + first_header
                    elif edition == 2:
                        length_octets = read_exact(stream, 8)
                        message_length = int.from_bytes(length_octets, "big")
                        header = prefix + first_header + length_octets
                    else:
                        raise DownloadError(
                            "A GRIB archive member uses an unsupported edition."
                        )
                    if (
                        message_length < len(header) + 4
                        or message_length > MAX_GRIB_MESSAGE_BYTES
                    ):
                        raise DownloadError(
                            "A GRIB message declares an invalid or unexpectedly large length."
                        )
                    message = header + read_exact(stream, message_length - len(header))
                    if message[-4:] != b"7777":
                        remaining = member_size - stream.tell()
                        if (
                            member_messages
                            or remaining <= 0
                            or member_size > MAX_GRIB_MESSAGE_BYTES
                        ):
                            raise DownloadError(
                                "A GRIB message has an invalid end marker."
                            )
                        tail = read_exact(stream, remaining)
                        complete_member = message + tail
                        if (
                            complete_member[-4:] != b"7777"
                            or complete_member.find(b"GRIB", 4) >= 0
                        ):
                            raise DownloadError(
                                "A GRIB message has an invalid end marker."
                            )
                        message_length_mismatches.append(
                            {
                                "member": member,
                                "header_declared_bytes": message_length,
                                "ecCodes_input_bytes": len(complete_member),
                            }
                        )
                        message = complete_member
                    handle = eccodes.codes_new_from_message(message)
                    if handle is None:
                        raise DownloadError("The ecCodes reader rejected a GRIB message.")
                    try:
                        message_count += 1
                        member_messages += 1
                        editions.add(edition)
                        short_name = get(handle, "shortName")
                        name = get(handle, "name")
                        units = get(handle, "units")
                        level_type = get(handle, "typeOfLevel")
                        level = get(handle, "level")
                        variable_key = (short_name, name, units, level_type, level)
                        variable_records[variable_key] = {
                            "short_name": short_name,
                            "name": name,
                            "units": units,
                            "type_of_level": level_type,
                            "level": level,
                        }

                        date_value = get(handle, "validityDate") or get(handle, "dataDate")
                        time_value = get(handle, "validityTime")
                        if time_value is None:
                            time_value = get(handle, "dataTime")
                        if date_value is not None and time_value is not None:
                            try:
                                timestamp = datetime.strptime(
                                    "%08d%04d" % (int(date_value), int(time_value)),
                                    "%Y%m%d%H%M",
                                ).replace(tzinfo=timezone.utc)
                                timestamps.add(timestamp)
                                variable_timestamps.setdefault(
                                    variable_key, set()
                                ).add(timestamp)
                            except (TypeError, ValueError):
                                pass

                        for key, output in (
                            ("latitudeOfFirstGridPointInDegrees", latitudes),
                            ("latitudeOfLastGridPointInDegrees", latitudes),
                            ("longitudeOfFirstGridPointInDegrees", longitudes),
                            ("longitudeOfLastGridPointInDegrees", longitudes),
                        ):
                            value = get(handle, key)
                            if value is not None:
                                try:
                                    output.append(float(value))
                                except (TypeError, ValueError):
                                    pass

                        grid_type = get(handle, "gridType")
                        if grid_type is not None:
                            grid_types.add(str(grid_type))
                        latitude_increment = get(
                            handle, "jDirectionIncrementInDegrees"
                        )
                        longitude_increment = get(
                            handle, "iDirectionIncrementInDegrees"
                        )
                        if (
                            latitude_increment is not None
                            and longitude_increment is not None
                        ):
                            try:
                                grid_increments.add(
                                    (
                                        abs(float(latitude_increment)),
                                        abs(float(longitude_increment)),
                                    )
                                )
                            except (TypeError, ValueError):
                                pass
                        earth_shape = get(handle, "shapeOfTheEarth")
                        if earth_shape is not None:
                            earth_shapes.add(str(earth_shape))
                        missing_marker = get(handle, "missingValue")
                        if missing_marker is not None:
                            missing_value_markers.add(str(missing_marker))
                        missing_count = get(handle, "numberOfMissing")
                        if missing_count is not None:
                            try:
                                missing_count_values.add(int(missing_count))
                            except (TypeError, ValueError):
                                pass
                        total_values = get(handle, "numberOfDataPoints")
                        if total_values is not None:
                            try:
                                total_value_counts.add(int(total_values))
                            except (TypeError, ValueError):
                                pass
                    finally:
                        eccodes.codes_release(handle)
            if not member_messages:
                raise DownloadError("A GRIB archive member contains no valid messages.")

    unique_times = sorted(timestamps)
    observed_intervals: set[int] = set()
    for key, times in variable_timestamps.items():
        ordered_times = sorted(times)
        variable = variable_records[key]
        variable["date_coverage_utc"] = {
            "start": ordered_times[0].isoformat(),
            "end": ordered_times[-1].isoformat(),
        }
        variable["distinct_timestamp_count"] = len(ordered_times)
        intervals = sorted(
            {
                int((right - left).total_seconds())
                for left, right in zip(ordered_times, ordered_times[1:])
            }
        )
        variable["time_resolution_seconds_observed"] = intervals
        observed_intervals.update(intervals)
    return {
        "format": "GRIB",
        "members": members,
        "message_count": message_count,
        "date_coverage_utc": {
            "start": unique_times[0].isoformat() if unique_times else None,
            "end": unique_times[-1].isoformat() if unique_times else None,
        },
        "time_resolution_seconds_observed": sorted(observed_intervals),
        "variables": list(variable_records.values()),
        "latitude_bounds_degrees": (
            [min(latitudes), max(latitudes)] if latitudes else None
        ),
        "longitude_bounds_degrees": (
            [min(longitudes), max(longitudes)] if longitudes else None
        ),
        "grid_types": sorted(grid_types),
        "grid_spacing_degrees_observed": [
            {"latitude": latitude, "longitude": longitude}
            for latitude, longitude in sorted(grid_increments)
        ],
        "grib_editions": sorted(editions),
        "earth_shape_codes": sorted(earth_shapes),
        "missing_value_markers": sorted(missing_value_markers),
        "number_of_missing_values_per_message": sorted(missing_count_values),
        "number_of_data_points_per_message": sorted(total_value_counts),
        "message_length_mismatches": message_length_mismatches,
        "coordinate_reference_information": (
            "GRIB gridType/shapeOfTheEarth keys recorded; no separate CRS declaration "
            "is assumed."
        ),
    }


def _netcdf_value(value: object) -> object:
    try:
        import numpy as np

        if isinstance(value, np.ndarray):
            return [_netcdf_value(item) for item in value.tolist()]
        if isinstance(value, np.generic):
            return _netcdf_value(value.item())
    except ImportError:
        pass
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, float) and not (-float("inf") < value < float("inf")):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _netcdf_attributes(attributes: object) -> dict[str, object]:
    internal_attributes = {
        "class",
        "name",
        "_netcdf4coordinates",
        "_netcdf4dimid",
        "dimension_list",
        "reference_list",
    }
    return {
        str(key): _netcdf_value(value)
        for key, value in attributes.items()  # type: ignore[attr-defined]
        if str(key).casefold() not in internal_attributes
    }


def _coordinate_bounds(
    chunks: object, fill_value: object = None
) -> tuple[float, float] | None:
    import numpy as np

    if isinstance(fill_value, list) and len(fill_value) == 1:
        fill_value = fill_value[0]
    if isinstance(fill_value, list):
        fill_value = None
    lower: float | None = None
    upper: float | None = None
    for chunk in chunks:  # type: ignore[union-attr]
        values = np.asarray(chunk)
        if values.size == 0:
            continue
        try:
            finite = values[np.isfinite(values)]
            if fill_value is not None:
                finite = finite[finite != fill_value]
        except TypeError:
            continue
        if finite.size:
            chunk_min = float(np.min(finite))
            chunk_max = float(np.max(finite))
            lower = chunk_min if lower is None else min(lower, chunk_min)
            upper = chunk_max if upper is None else max(upper, chunk_max)
    return (lower, upper) if lower is not None and upper is not None else None


def _coordinate_spacing(chunks: object) -> list[float]:
    import numpy as np

    previous: float | None = None
    spacings: set[float] = set()
    for chunk in chunks:  # type: ignore[union-attr]
        for raw_value in np.asarray(chunk).reshape(-1):
            value = float(raw_value)
            if not np.isfinite(value):
                continue
            if previous is not None:
                spacing = round(abs(value - previous), 8)
                if spacing:
                    spacings.add(spacing)
            previous = value
    return sorted(spacings)


def _read_hdf5_chunks(dataset: object) -> object:
    shape = dataset.shape  # type: ignore[attr-defined]
    if not shape:
        yield dataset[()]  # type: ignore[index]
        return
    for start in range(0, shape[0], 64):
        selection = (slice(start, min(start + 64, shape[0])),) + tuple(
            slice(None) for _ in shape[1:]
        )
        yield dataset[selection]  # type: ignore[index]


def _decode_netcdf_time(
    values: tuple[float, float] | None, units: object, calendar: object
) -> dict[str, object] | None:
    if values is None or not isinstance(units, str):
        return None
    if str(calendar or "standard").casefold() not in {
        "standard",
        "gregorian",
        "proleptic_gregorian",
    }:
        return None
    match = re.fullmatch(
        r"\s*(seconds?|minutes?|hours?|days?)\s+since\s+(.+?)\s*",
        units,
        re.IGNORECASE,
    )
    if not match:
        return None
    unit_seconds = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }[match.group(1).casefold().rstrip("s")]
    try:
        base = datetime.fromisoformat(match.group(2).replace("Z", "+00:00"))
    except ValueError:
        return None
    if base.tzinfo is None:
        base = base.replace(tzinfo=timezone.utc)
    return {
        "start": (base + timedelta(seconds=values[0] * unit_seconds)).isoformat(),
        "end": (base + timedelta(seconds=values[1] * unit_seconds)).isoformat(),
    }


def _time_unit_seconds(units: object) -> int | None:
    if not isinstance(units, str):
        return None
    match = re.match(r"\s*(seconds?|minutes?|hours?|days?)\b", units, re.IGNORECASE)
    if not match:
        return None
    return {
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
    }[match.group(1).casefold().rstrip("s")]


def _cdf_read_exact(stream: object, size: int) -> bytes:
    data = stream.read(size)  # type: ignore[attr-defined]
    if len(data) != size:
        raise DownloadError("A NetCDF classic header is truncated.")
    return data


def _cdf_read_int(stream: object) -> int:
    return struct.unpack(">i", _cdf_read_exact(stream, 4))[0]


def _cdf_read_name(stream: object) -> str:
    length = _cdf_read_int(stream)
    if length < 0 or length > 1024 * 1024:
        raise DownloadError("A NetCDF classic name has an invalid length.")
    name = _cdf_read_exact(stream, length).decode("utf-8", errors="replace")
    padding = (-length) % 4
    if padding:
        _cdf_read_exact(stream, padding)
    return name


def _cdf_read_list_count(stream: object, expected_tag: int) -> int:
    tag = _cdf_read_int(stream)
    count = _cdf_read_int(stream)
    if tag == 0 and count == 0:
        return 0
    if tag != expected_tag or count < 0 or count > 100000:
        raise DownloadError("A NetCDF classic header contains an invalid list.")
    return count


def _cdf_read_attributes(stream: object) -> dict[str, object]:
    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}
    type_formats = {1: "b", 3: "h", 4: "i", 5: "f", 6: "d"}
    attributes: dict[str, object] = {}
    for _ in range(_cdf_read_list_count(stream, 12)):
        name = _cdf_read_name(stream)
        type_code = _cdf_read_int(stream)
        count = _cdf_read_int(stream)
        if type_code not in type_sizes or count < 0:
            raise DownloadError("A NetCDF classic attribute has an invalid type or size.")
        byte_count = count * type_sizes[type_code]
        if byte_count > 16 * 1024 * 1024:
            raise DownloadError("A NetCDF classic attribute is unexpectedly large.")
        raw = _cdf_read_exact(stream, byte_count)
        padding = (-byte_count) % 4
        if padding:
            _cdf_read_exact(stream, padding)
        if type_code == 2:
            value: object = raw.decode("utf-8", errors="replace")
        else:
            values = struct.unpack(">%d%s" % (count, type_formats[type_code]), raw)
            value = values[0] if count == 1 else list(values)
        attributes[name] = _netcdf_value(value)
    return attributes


def _read_cdf_metadata(stream: object, member_name: str) -> dict[str, object]:
    signature = _cdf_read_exact(stream, 4)
    edition = signature[3]
    if signature[:3] != b"CDF" or edition not in {1, 2}:
        raise DownloadError("The NetCDF classic member uses an unsupported format.")
    num_records = struct.unpack(">I", _cdf_read_exact(stream, 4))[0]
    dimensions: list[dict[str, object]] = []
    for _ in range(_cdf_read_list_count(stream, 10)):
        name = _cdf_read_name(stream)
        length = _cdf_read_int(stream)
        dimensions.append({"name": name, "length": length})
    global_attributes = _cdf_read_attributes(stream)
    variables: list[dict[str, object]] = []
    type_sizes = {1: 1, 2: 1, 3: 2, 4: 4, 5: 4, 6: 8}
    type_formats = {1: "b", 2: "c", 3: "h", 4: "i", 5: "f", 6: "d"}
    for _ in range(_cdf_read_list_count(stream, 11)):
        name = _cdf_read_name(stream)
        dimension_count = _cdf_read_int(stream)
        if dimension_count < 0 or dimension_count > len(dimensions):
            raise DownloadError("A NetCDF classic variable has invalid dimensions.")
        dimension_ids = [
            _cdf_read_int(stream) for _ in range(dimension_count)
        ]
        if any(index < 0 or index >= len(dimensions) for index in dimension_ids):
            raise DownloadError("A NetCDF classic variable references an invalid dimension.")
        attributes = _cdf_read_attributes(stream)
        type_code = _cdf_read_int(stream)
        size = struct.unpack(">I", _cdf_read_exact(stream, 4))[0]
        if type_code not in type_sizes:
            raise DownloadError("A NetCDF classic variable has an unsupported type.")
        begin = struct.unpack(">Q", _cdf_read_exact(stream, 8))[0] if edition == 2 else struct.unpack(">I", _cdf_read_exact(stream, 4))[0]
        shape = [
            num_records if dimensions[index]["length"] == 0 else dimensions[index]["length"]
            for index in dimension_ids
        ]
        variables.append(
            {
                "name": name,
                "dimensions": [str(dimensions[index]["name"]) for index in dimension_ids],
                "shape": shape,
                "type_code": type_code,
                "type_size": type_sizes[type_code],
                "type_format": type_formats[type_code],
                "vsize": size,
                "begin": begin,
                "attributes": attributes,
            }
        )

    record_dimension_ids = {
        index for index, dimension in enumerate(dimensions) if dimension["length"] == 0
    }
    record_dimension_names = {
        str(dimensions[index]["name"]) for index in record_dimension_ids
    }
    record_variables = [
        variable
        for variable in variables
        if variable["dimensions"]
        and variable["dimensions"][0] in record_dimension_names
    ]
    record_size = sum(int(variable["vsize"]) for variable in record_variables)
    coordinate_records: dict[str, dict[str, object]] = {}
    for variable in variables:
        name = str(variable["name"])
        if name.casefold() not in {"latitude", "lat", "longitude", "lon", "time"}:
            continue
        shape = [int(value) for value in variable["shape"]]
        if len(shape) != 1 or shape[0] > 10_000_000:
            continue
        record_variable = bool(
            variable["dimensions"]
            and variable["dimensions"][0]
            in {
                str(dimensions[index]["name"])
                for index in record_dimension_ids
            }
        )
        count = shape[0]
        element_size = int(variable["type_size"])
        lower: float | None = None
        upper: float | None = None
        previous: float | None = None
        intervals: set[int] = set()
        spacings: set[float] = set()
        time_factor = _time_unit_seconds(variable["attributes"].get("units"))

        def include_values(values: object) -> None:
            nonlocal lower, upper, previous
            for value in values:  # type: ignore[union-attr]
                numeric = float(value)
                if numeric != numeric or abs(numeric) == float("inf"):
                    continue
                fill_value = variable["attributes"].get("_FillValue")
                if isinstance(fill_value, (int, float)) and numeric == fill_value:
                    continue
                lower = numeric if lower is None else min(lower, numeric)
                upper = numeric if upper is None else max(upper, numeric)
                if (
                    name.casefold() == "time"
                    and previous is not None
                    and time_factor is not None
                ):
                    intervals.add(round((numeric - previous) * time_factor))
                if name.casefold() in {"latitude", "lat", "longitude", "lon"} and previous is not None:
                    spacing = round(abs(numeric - previous), 8)
                    if spacing:
                        spacings.add(spacing)
                previous = numeric

        if record_variable:
            if record_size <= 0 or element_size > record_size:
                raise DownloadError("A NetCDF classic record layout is invalid.")
            for index in range(count):
                stream.seek(int(variable["begin"]) + index * record_size)  # type: ignore[attr-defined]
                raw = _cdf_read_exact(stream, element_size)
                include_values(
                    [struct.unpack(">" + str(variable["type_format"]), raw)[0]]
                )
        else:
            stream.seek(int(variable["begin"]))  # type: ignore[attr-defined]
            remaining = count
            while remaining:
                batch_count = min(remaining, 8192)
                raw = _cdf_read_exact(stream, batch_count * element_size)
                include_values(
                    struct.unpack(
                        ">%d%s" % (batch_count, variable["type_format"]), raw
                    )
                )
                padding = (-(batch_count * element_size)) % 4
                if remaining == batch_count and padding:
                    _cdf_read_exact(stream, padding)
                remaining -= batch_count
        bounds = (
            [lower, upper] if lower is not None and upper is not None else None
        )
        coordinate_records[name] = {
            "units": variable["attributes"].get("units"),
            "bounds": bounds,
            "count": count,
            "attributes": variable["attributes"],
        }
        if spacings:
            coordinate_records[name]["spacing_degrees_observed"] = sorted(spacings)
        if name.casefold() == "time":
            time_range = (lower, upper) if lower is not None and upper is not None else None
            coordinate_records[name]["date_coverage_utc"] = _decode_netcdf_time(
                time_range,
                variable["attributes"].get("units"),
                variable["attributes"].get("calendar"),
            )
            if intervals:
                coordinate_records[name]["time_resolution_seconds_observed"] = sorted(
                    intervals
                )

    output_variables = [
        {
            "name": variable["name"],
            "dimensions": variable["dimensions"],
            "shape": variable["shape"],
            "units": variable["attributes"].get("units"),
            "long_name": variable["attributes"].get("long_name"),
            "standard_name": variable["attributes"].get("standard_name"),
            "missing_value": variable["attributes"].get("missing_value"),
            "fill_value": variable["attributes"].get("_FillValue"),
            "grid_mapping": variable["attributes"].get("grid_mapping"),
            "attributes": variable["attributes"],
        }
        for variable in variables
    ]
    return {
        "filename": member_name,
        "format": "NetCDF classic 64-bit offset" if edition == 2 else "NetCDF classic",
        "global_attributes": global_attributes,
        "variables": output_variables,
        "coordinates": coordinate_records,
        "coordinate_reference_information": {
            key: value
            for key, value in global_attributes.items()
            if key.casefold() in {"crs", "geotransform", "spatial_ref", "projection"}
        },
    }


def _read_netcdf_metadata(
    path: Path, contents: list[dict[str, object]]
) -> dict[str, object] | None:
    members = [
        str(item["name"])
        for item in contents
        if Path(str(item["name"])).suffix.casefold() == ".nc"
    ]
    if not members:
        return None

    try:
        import h5py
    except ImportError:
        h5py = None
    import numpy as np

    files: list[dict[str, object]] = []
    all_variables: list[dict[str, object]] = []
    latitude_bounds: list[tuple[float, float]] = []
    longitude_bounds: list[tuple[float, float]] = []
    date_ranges: list[dict[str, object]] = []
    time_intervals: set[int] = set()
    coordinate_references: list[dict[str, object]] = []

    try:
        with zipfile.ZipFile(path) as archive:
            for member in members:
                with archive.open(member, "r") as stream:
                    signature = stream.read(8)
                    stream.seek(0)
                    if signature.startswith(b"CDF"):
                        file_metadata = _read_cdf_metadata(stream, member)
                    elif signature == bytes.fromhex("894844460d0a1a0a"):
                        if h5py is None:
                            raise DownloadError(
                                "NetCDF-4/HDF5 members were found but h5py is unavailable."
                            )
                        with h5py.File(stream, "r") as dataset:
                            global_attributes = _netcdf_attributes(dataset.attrs)
                            variables: list[dict[str, object]] = []
                            coordinates: dict[str, dict[str, object]] = {}
                            references: list[dict[str, object]] = []

                            def inspect(name: str, item: object) -> None:
                                if not isinstance(item, h5py.Dataset):
                                    return
                                attributes = _netcdf_attributes(item.attrs)
                                dimensions = []
                                for axis in item.dims:
                                    scales = list(axis.keys())
                                    dimensions.append(
                                        axis.label
                                        or (
                                            Path(scales[0]).name
                                            if scales
                                            else None
                                        )
                                    )
                                record = {
                                    "name": name,
                                    "dimensions": dimensions,
                                    "shape": list(item.shape),
                                    "units": attributes.get("units"),
                                    "long_name": attributes.get("long_name"),
                                    "standard_name": attributes.get("standard_name"),
                                    "missing_value": attributes.get("missing_value"),
                                    "fill_value": attributes.get("_FillValue"),
                                    "grid_mapping": attributes.get("grid_mapping"),
                                    "attributes": attributes,
                                }
                                variables.append(record)
                                all_variables.append(
                                    {"file": member, **record}
                                )
                                folded = Path(name).name.casefold()
                                if folded in {
                                    "latitude",
                                    "lat",
                                    "longitude",
                                    "lon",
                                    "time",
                                    "valid_time",
                                }:
                                    bounds = _coordinate_bounds(
                                        _read_hdf5_chunks(item),
                                        attributes.get("_FillValue"),
                                    )
                                    coordinate = {
                                        "units": attributes.get("units"),
                                        "bounds": list(bounds) if bounds else None,
                                        "count": int(item.size),
                                        "attributes": attributes,
                                    }
                                    if folded in {
                                        "latitude",
                                        "lat",
                                        "longitude",
                                        "lon",
                                    } and item.ndim == 1:
                                        spacing = _coordinate_spacing(
                                            _read_hdf5_chunks(item)
                                        )
                                        if spacing:
                                            coordinate[
                                                "spacing_degrees_observed"
                                            ] = spacing
                                    if folded in {"time", "valid_time"}:
                                        coordinate["date_coverage_utc"] = (
                                            _decode_netcdf_time(
                                                bounds,
                                                attributes.get("units"),
                                                attributes.get("calendar"),
                                            )
                                        )
                                        time_factor = _time_unit_seconds(
                                            attributes.get("units")
                                        )
                                        if item.size > 1 and time_factor is not None:
                                            previous: float | None = None
                                            intervals: set[int] = set()
                                            for chunk in _read_hdf5_chunks(item):
                                                values = np.asarray(chunk).reshape(-1)
                                                for raw_value in values:
                                                    value = float(raw_value)
                                                    if not np.isfinite(value):
                                                        continue
                                                    if previous is not None:
                                                        intervals.add(
                                                            round(
                                                                (value - previous)
                                                                * time_factor
                                                            )
                                                        )
                                                    previous = value
                                            coordinate[
                                                "time_resolution_seconds_observed"
                                            ] = sorted(intervals)
                                    coordinates[Path(name).name] = coordinate
                                    if bounds and folded in {"latitude", "lat"}:
                                        latitude_bounds.append(bounds)
                                    if bounds and folded in {"longitude", "lon"}:
                                        longitude_bounds.append(bounds)
                                    if folded in {"time", "valid_time"}:
                                        coverage = coordinate.get("date_coverage_utc")
                                        if (
                                            isinstance(coverage, dict)
                                            and (
                                                folded == "valid_time"
                                                or int(coordinate["count"]) > 1
                                            )
                                        ):
                                            date_ranges.append(coverage)
                                        intervals = coordinate.get(
                                            "time_resolution_seconds_observed", []
                                        )
                                        time_intervals.update(
                                            int(value) for value in intervals
                                        )
                                if any(
                                    key.casefold()
                                    in {"grid_mapping_name", "spatial_ref", "crs_wkt"}
                                    for key in attributes
                                ):
                                    references.append(
                                        {"variable": name, "attributes": attributes}
                                    )

                            dataset.visititems(inspect)
                            file_metadata = {
                                "filename": member,
                                "format": "NetCDF-4/HDF5",
                                "global_attributes": global_attributes,
                                "variables": variables,
                                "coordinates": coordinates,
                                "coordinate_reference_information": references,
                            }
                            coordinate_references.extend(
                                {
                                    "file": member,
                                    **reference,
                                }
                                for reference in references
                            )
                    else:
                        raise DownloadError(
                            "A NetCDF member is not a supported classic or HDF5 format."
                        )
                if str(file_metadata.get("format", "")).startswith("NetCDF classic"):
                    for name, coordinate in file_metadata["coordinates"].items():
                        bounds = coordinate.get("bounds")
                        if bounds and name.casefold() in {"latitude", "lat"}:
                            latitude_bounds.append(tuple(bounds))
                        if bounds and name.casefold() in {"longitude", "lon"}:
                            longitude_bounds.append(tuple(bounds))
                        coverage = coordinate.get("date_coverage_utc")
                        if (
                            isinstance(coverage, dict)
                            and (
                                name.casefold() == "valid_time"
                                or int(coordinate.get("count", 0)) > 1
                            )
                        ):
                            date_ranges.append(coverage)
                        time_intervals.update(
                            int(value)
                            for value in coordinate.get(
                                "time_resolution_seconds_observed", []
                            )
                        )
                    all_variables.extend(
                        {"file": member, **variable}
                        for variable in file_metadata["variables"]
                    )
                    if file_metadata["coordinate_reference_information"]:
                        coordinate_references.append(
                            {
                                "file": member,
                                **file_metadata["coordinate_reference_information"],
                            }
                        )
                files.append(file_metadata)
    except (OSError, ValueError, zipfile.BadZipFile, struct.error):
        raise DownloadError("NetCDF metadata inspection failed.") from None

    def merged_bounds(bounds: list[tuple[float, float]]) -> list[float] | None:
        return (
            [min(item[0] for item in bounds), max(item[1] for item in bounds)]
            if bounds
            else None
        )

    starts = [
        str(item["start"])
        for item in date_ranges
        if item.get("start") is not None
    ]
    ends = [
        str(item["end"])
        for item in date_ranges
        if item.get("end") is not None
    ]
    return {
        "format": "NetCDF",
        "files": files,
        "variables": all_variables,
        "missing_value_counts_computed": False,
        "missing_value_count_limitation": (
            "Fill and missing-value attributes were inspected, but data variables were "
            "not scanned for per-cell missing-value counts."
        ),
        "date_coverage_utc": {
            "start": min(starts) if starts else None,
            "end": max(ends) if ends else None,
        },
        "time_resolution_seconds_observed": sorted(time_intervals),
        "latitude_bounds_degrees": merged_bounds(latitude_bounds),
        "longitude_bounds_degrees": merged_bounds(longitude_bounds),
        "coordinate_reference_information": coordinate_references,
    }


def _inspect_weather(
    path: Path, contents: list[dict[str, object]]
) -> dict[str, object]:
    metadata = _read_grib_metadata(path, contents)
    if metadata is not None:
        return metadata
    metadata = _read_netcdf_metadata(path, contents)
    if metadata is not None:
        return metadata
    file_members = [
        str(item["name"])
        for item in contents
        if not item["is_directory"]
    ]
    return {
        "status": "UNAVAILABLE",
        "reason": (
            "No GRIB members were found. NetCDF/other scientific formats require "
            "format-specific metadata inspection."
        ),
        "archive_file_members": file_members,
    }


def main() -> int:
    if MANIFEST_PATH.exists():
        raise DownloadError(
            "Refusing to overwrite the existing provenance manifest: %s"
            % MANIFEST_PATH.relative_to(PROJECT_ROOT)
        )

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    metadata: list[dict[str, object]] = []
    staged_archives: list[tuple[Path, Path]] = []
    for request in REQUESTS:
        target = DOWNLOAD_DIR / str(request["filename"])
        print(
            "Checking request %d (%s); download URL is redacted."
            % (request["request_number"], request["request_reference"])
        )
        remote_length, supports_ranges, content_type = _head(str(request["url"]))
        if content_type and "zip" not in content_type.casefold() and "octet-stream" not in content_type.casefold():
            raise DownloadError("The official object store did not identify a ZIP archive.")
        if remote_length is not None:
            print(
                "Server size: %s bytes (%.2f MiB); byte-range resume: %s."
                % (remote_length, remote_length / (1024 * 1024), "yes" if supports_ranges else "no")
            )
        print(
            "Downloading to %s"
            % target.relative_to(PROJECT_ROOT).as_posix()
        )
        expected_approx_size = str(request["user_reported_approx_size"])
        if remote_length is not None:
            if request["request_number"] == 1 and remote_length < 1_000_000_000:
                print(
                    "WARNING: request 1 link size is below 1 GB, unlike its "
                    "user-reported 2.03 GB."
                )
            elif request["request_number"] == 2 and remote_length > 1_000_000_000:
                print(
                    "WARNING: request 2 link size is above 1 GB, unlike its "
                    "user-reported 647 MB."
                )
        partial = target.with_suffix(target.suffix + ".part")
        actual_size = _download(request, target, remote_length, supports_ranges)
        contents, zip_ok = _zip_inventory(partial)
        if not zip_ok:
            raise DownloadError(
                "ZIP CRC validation failed for %s; the archive was retained for diagnosis."
                % target.name
            )
        checksum = _sha256(partial)
        print(
            "Validated %s: %d bytes; SHA-256 %s; ZIP CRC OK."
            % (target.name, actual_size, checksum)
        )
        print("Archive members:")
        for item in contents:
            print("  %s (%s bytes)" % (item["name"], item["size_bytes"]))
        weather_metadata = _inspect_weather(partial, contents)
        print(
            "Weather metadata: %s"
            % json.dumps(weather_metadata, ensure_ascii=False, separators=(",", ":"))
        )

        metadata.append(
            {
                "request_number": request["request_number"],
                "request_reference": request["request_reference"],
                "user_reported_approx_size": expected_approx_size,
                "request_status": "Successful (reported by user; MHT not independently inspected)",
                "source_url": DATASET_URL,
                "download_host": ALLOWED_HOST,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "filename": target.name,
                "local_path": target.relative_to(PROJECT_ROOT).as_posix(),
                "size_bytes": actual_size,
                "sha256": checksum,
                "content_length_verified": remote_length is None or actual_size == remote_length,
                "zip_format_valid": True,
                "zip_crc_valid": zip_ok,
                "archive_contents": contents,
                "weather_metadata": weather_metadata,
            }
        )
        staged_archives.append((partial, target))

    manifest = {
        "dataset_id": "era5_land",
        "dataset_name": "ERA5-Land hourly data from 1950 to present",
        "source_url": DATASET_URL,
        "requests": metadata,
        "license": {
            "name": "Licence to Use Copernicus Products v1.2",
            "version": "November 2019",
            "license_url": LICENSE_URL,
            "cds_terms_url": CDS_TERMS_URL,
            "attribution": ATTRIBUTION,
            "third_party_data_exceptions": (
                "Third-party products or information directly accessible through Copernicus "
                "portals may be subject to separate licence terms."
            ),
        },
        "request_metadata_limitations": [
            "The CDS request-history MHT was not parsed in this run; exact request parameters "
            "such as variables, dates and geographic bounds are not independently available "
            "from the supplied object URLs. Metadata reported above is derived from the files.",
            "The actual server sizes are reversed relative to the user-reported approximate "
            "request sizes; request numbering follows the order of the supplied URLs.",
        ],
    }
    for partial, target in staged_archives:
        try:
            partial.rename(target)
        except OSError:
            raise DownloadError(
                "Could not finalize an archive without overwriting an existing file."
            ) from None
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        with MANIFEST_PATH.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
    except FileExistsError:
        raise DownloadError("Refusing to overwrite the existing provenance manifest.") from None
    print(
        "Manifest created: %s"
        % MANIFEST_PATH.relative_to(PROJECT_ROOT).as_posix()
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DownloadError as error:
        print("ERROR: %s" % error, file=sys.stderr)
        raise SystemExit(1)
