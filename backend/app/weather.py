"""Provider adapters for historical weather estimates and opt-in forecasts."""

from datetime import date, datetime, timedelta, timezone
from threading import Lock
from time import monotonic
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, Query

from app.config import get_settings
from app.security import current_user

router = APIRouter(
    prefix="/api/v1/weather",
    tags=["weather"],
    dependencies=[Depends(current_user)],
)
NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
NASA_POWER_MONTHLY_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NASA_PARAMETERS = (
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "PRECTOTCORR",
    "RH2M",
    "WS2M",
    "ALLSKY_SFC_SW_DWN",
)
NASA_UNITS = {
    "T2M": "degC",
    "T2M_MAX": "degC",
    "T2M_MIN": "degC",
    "PRECTOTCORR": "mm/day",
    "RH2M": "%",
    "WS2M": "m/s",
    "ALLSKY_SFC_SW_DWN": "MJ/m^2/day",
}
FORECAST_PARAMETERS = (
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "shortwave_radiation",
)
FORECAST_UNITS = {
    "temperature_2m": "degC",
    "relative_humidity_2m": "%",
    "precipitation": "mm",
    "wind_speed_10m": "km/h",
    "shortwave_radiation": "W/m^2",
}
DAILY_FORECAST_PARAMETERS = (
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "precipitation_probability_max",
    "wind_speed_10m_max",
)
DAILY_FORECAST_UNITS = {
    "temperature_2m_max": "degC",
    "temperature_2m_min": "degC",
    "precipitation_sum": "mm",
    "precipitation_probability_max": "%",
    "wind_speed_10m_max": "km/h",
}
CACHE_TTL_SECONDS = 6 * 60 * 60
CACHE_MONTHLY_TTL_SECONDS = 24 * 60 * 60
CACHE_CURRENT_TTL_SECONDS = 10 * 60
CACHE_MAX_ENTRIES = 256
_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_cache_lock = Lock()


class WeatherProviderError(Exception):
    """Raised when an upstream response is unavailable or malformed."""


def _request_json(url: str, cache_ttl: int) -> dict[str, Any]:
    now = monotonic()
    with _cache_lock:
        cached = _cache.get(url)
        if cached and cached[0] > now:
            return cached[1]
        if cached:
            del _cache[url]

    request = Request(url, headers={"Accept": "application/json", "User-Agent": "AgroSense-360/0.1"})
    try:
        with urlopen(request, timeout=20) as response:
            if response.status != 200:
                raise WeatherProviderError(f"Weather provider returned HTTP {response.status}.")
            payload = response.read(8 * 1024 * 1024 + 1)
    except (OSError, URLError) as error:
        raise WeatherProviderError("Weather provider could not be reached.") from error
    if len(payload) > 8 * 1024 * 1024:
        raise WeatherProviderError("Weather provider response exceeded the size limit.")
    try:
        import json

        decoded = json.loads(payload)
    except (UnicodeDecodeError, ValueError) as error:
        raise WeatherProviderError("Weather provider returned invalid JSON.") from error
    if not isinstance(decoded, dict):
        raise WeatherProviderError("Weather provider returned an unexpected response.")

    with _cache_lock:
        if len(_cache) >= CACHE_MAX_ENTRIES:
            oldest = min(_cache, key=lambda key: _cache[key][0])
            del _cache[oldest]
        _cache[url] = (monotonic() + cache_ttl, decoded)
    return decoded


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    if not (-1e6 < result < 1e6) or result == -999.0:
        return None
    return result


def _validate_coordinate(latitude: float, longitude: float) -> None:
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise HTTPException(status_code=422, detail="Coordinates are outside valid latitude/longitude ranges.")


def _provider_error(error: WeatherProviderError) -> HTTPException:
    return HTTPException(status_code=502, detail=str(error))


@router.get("/current")
def current_weather(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> dict[str, Any]:
    """Return Open-Meteo's current model estimate when its non-commercial use is enabled."""
    _validate_coordinate(latitude, longitude)
    if not get_settings().open_meteo_noncommercial_enabled:
        raise HTTPException(
            status_code=503,
            detail=(
                "Current weather is unavailable. Enable Open-Meteo only when the intended use "
                "qualifies under its free non-commercial terms."
            ),
        )

    parameters = ("temperature_2m", "relative_humidity_2m", "precipitation", "wind_speed_10m")
    units_fallback = {
        "temperature_2m": "degC",
        "relative_humidity_2m": "%",
        "precipitation": "mm",
        "wind_speed_10m": "km/h",
    }
    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(parameters),
            "timezone": "UTC",
        }
    )
    try:
        payload = _request_json(f"{OPEN_METEO_URL}?{query}", CACHE_CURRENT_TTL_SECONDS)
        current = payload["current"]
        units = payload["current_units"]
        if (
            not isinstance(current, dict)
            or not isinstance(current.get("time"), str)
            or not isinstance(units, dict)
        ):
            raise TypeError
        values = {key: _number(current.get(key)) for key in parameters}
        if not any(value is not None for value in values.values()):
            raise TypeError
    except WeatherProviderError as error:
        raise _provider_error(error) from error
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise HTTPException(status_code=502, detail="Open-Meteo returned invalid current conditions.") from error

    return {
        "provider": "Open-Meteo",
        "source_url": "https://open-meteo.com/",
        "attribution": (
            "Weather data by Open-Meteo.com; API data CC BY 4.0. Current conditions are model estimates, "
            "not direct station observations."
        ),
        "data_kind": "current_model_estimate",
        "time_standard": "UTC",
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": current["time"],
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "units": {key: units.get(key, units_fallback[key]) for key in parameters},
        "values": values,
        "cached_for_seconds": CACHE_CURRENT_TTL_SECONDS,
    }


@router.get("/history")
def historical_weather(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    start_date: date = Query(),
    end_date: date = Query(),
) -> dict[str, Any]:
    """Return daily NASA POWER gridded estimates; these are not station observations."""
    _validate_coordinate(latitude, longitude)
    today = date.today()
    if start_date < date(1981, 1, 1):
        raise HTTPException(status_code=422, detail="NASA POWER daily data starts on 1981-01-01.")
    if end_date < start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date.")
    if end_date > today - timedelta(days=2):
        raise HTTPException(status_code=422, detail="Select an end date at least two days in the past.")
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=422, detail="A single request is limited to 366 daily records.")

    query = urlencode(
        {
            "parameters": ",".join(NASA_PARAMETERS),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d"),
            "format": "JSON",
            "time-standard": "UTC",
        }
    )
    try:
        payload = _request_json(f"{NASA_POWER_URL}?{query}", CACHE_TTL_SECONDS)
        properties = payload["properties"]
        parameters = properties["parameter"]
        if not isinstance(parameters, dict):
            raise TypeError
        dates = sorted(set().union(*(set(values) for values in parameters.values())))
        records = [
            {
                "timestamp": f"{day[:4]}-{day[4:6]}-{day[6:8]}T00:00:00Z",
                "values": {
                    parameter: _number(parameters.get(parameter, {}).get(day))
                    for parameter in NASA_PARAMETERS
                },
            }
            for day in dates
        ]
    except WeatherProviderError as error:
        raise _provider_error(error) from error
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise HTTPException(status_code=502, detail="NASA POWER returned an invalid daily time series.") from error

    return {
        "provider": "NASA POWER",
        "source_url": "https://power.larc.nasa.gov/",
        "attribution": "Source: NASA POWER. Gridded meteorological/solar estimates; not direct ground observations.",
        "data_kind": "historical_gridded_estimate",
        "time_standard": "UTC",
        "latitude": latitude,
        "longitude": longitude,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "units": NASA_UNITS,
        "records": records,
        "cached_for_seconds": CACHE_TTL_SECONDS,
    }


@router.get("/climate-monthly")
def monthly_climate(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    start_year: int = Query(ge=1981),
    end_year: int = Query(ge=1981),
) -> dict[str, Any]:
    """Return NASA POWER multi-year monthly means, not station observations or crop suitability."""
    _validate_coordinate(latitude, longitude)
    if end_year < start_year:
        raise HTTPException(status_code=422, detail="end_year must be on or after start_year.")
    if end_year > date.today().year - 1:
        raise HTTPException(
            status_code=422,
            detail="Select a final year no later than the previous year for complete meteorological data.",
        )
    if end_year - start_year > 29:
        raise HTTPException(status_code=422, detail="Monthly climate requests are limited to 30 years.")

    query = urlencode(
        {
            "parameters": ",".join(NASA_PARAMETERS),
            "community": "AG",
            "longitude": longitude,
            "latitude": latitude,
            "start": start_year,
            "end": end_year,
            "format": "JSON",
        }
    )
    try:
        payload = _request_json(f"{NASA_POWER_MONTHLY_URL}?{query}", CACHE_MONTHLY_TTL_SECONDS)
        parameters = payload["properties"]["parameter"]
        if not isinstance(parameters, dict):
            raise TypeError

        monthly_values: dict[int, dict[str, list[float]]] = {
            month: {parameter: [] for parameter in NASA_PARAMETERS}
            for month in range(1, 13)
        }
        for parameter in NASA_PARAMETERS:
            series = parameters.get(parameter, {})
            if not isinstance(series, dict):
                raise TypeError
            for period, raw_value in series.items():
                if (
                    not isinstance(period, str)
                    or len(period) != 6
                    or not period.isdigit()
                    or not start_year <= int(period[:4]) <= end_year
                    or not 1 <= int(period[4:]) <= 12
                ):
                    continue
                value = _number(raw_value)
                if value is not None:
                    monthly_values[int(period[4:])][parameter].append(value)

        records = [
            {
                "month": month,
                "values": {
                    parameter: (
                        sum(values) / len(values) if values else None
                    )
                    for parameter, values in monthly_values[month].items()
                },
                "years_with_data": {
                    parameter: len(values)
                    for parameter, values in monthly_values[month].items()
                },
            }
            for month in range(1, 13)
        ]
        metadata = payload.get("parameters", {})
        if not isinstance(metadata, dict):
            metadata = {}
        units = {
            parameter: (
                metadata.get(parameter, {}).get("units", NASA_UNITS[parameter])
                if isinstance(metadata.get(parameter, {}), dict)
                else NASA_UNITS[parameter]
            )
            for parameter in NASA_PARAMETERS
        }
        header = payload.get("header", {})
        if not isinstance(header, dict):
            header = {}
        time_standard = header.get("time_standard", "LST")
        if not isinstance(time_standard, str) or not time_standard:
            raise TypeError
        source_datasets = header.get("sources", [])
        if not isinstance(source_datasets, list) or any(not isinstance(item, str) for item in source_datasets):
            source_datasets = []
    except WeatherProviderError as error:
        raise _provider_error(error) from error
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError) as error:
        raise HTTPException(status_code=502, detail="NASA POWER returned an invalid monthly time series.") from error

    return {
        "provider": "NASA POWER",
        "source_url": "https://power.larc.nasa.gov/",
        "attribution": (
            "Source: NASA POWER. Monthly meteorological and solar estimates derived from source products; "
            "not direct ground observations. Means are calculated across available years for each calendar month."
        ),
        "data_kind": "multi_year_monthly_gridded_estimate",
        "time_standard": time_standard,
        "source_datasets": source_datasets,
        "latitude": latitude,
        "longitude": longitude,
        "start_year": start_year,
        "end_year": end_year,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "units": units,
        "records": records,
        "cached_for_seconds": CACHE_MONTHLY_TTL_SECONDS,
        "limitation": (
            "This is descriptive climate context only. It is not a crop suitability assessment; "
            "verified crop-specific thresholds, local soil measurements, and field validation are required."
        ),
    }


@router.get("/forecast")
def weather_forecast(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> dict[str, Any]:
    """Return an opt-in free forecast only when non-commercial use is explicitly enabled."""
    _validate_coordinate(latitude, longitude)
    if not get_settings().open_meteo_noncommercial_enabled:
        raise HTTPException(
            status_code=503,
            detail=(
                "Open-Meteo forecast is disabled. Enable it only for qualifying non-commercial use "
                "and provide CC BY 4.0 attribution."
            ),
        )

    query = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(FORECAST_PARAMETERS),
            "daily": ",".join(DAILY_FORECAST_PARAMETERS),
            "forecast_days": 7,
            "timezone": "UTC",
        }
    )
    try:
        payload = _request_json(f"{OPEN_METEO_URL}?{query}", 10 * 60)
        hourly = payload["hourly"]
        times = hourly["time"]
        if (
            not isinstance(times, list)
            or not times
            or len(times) > 24 * 7
            or any(not isinstance(timestamp, str) for timestamp in times)
        ):
            raise TypeError
        columns = {key: hourly.get(key) for key in FORECAST_PARAMETERS}
        if any(not isinstance(values, list) or len(values) != len(times) for values in columns.values()):
            raise TypeError
        daily = payload["daily"]
        daily_times = daily["time"]
        if (
            not isinstance(daily_times, list)
            or not 1 <= len(daily_times) <= 7
            or any(not isinstance(day, str) for day in daily_times)
        ):
            raise TypeError
        daily_columns = {key: daily.get(key) for key in DAILY_FORECAST_PARAMETERS}
        if any(not isinstance(values, list) or len(values) != len(daily_times) for values in daily_columns.values()):
            raise TypeError
        records = [
            {
                "timestamp": timestamp,
                "values": {key: _number(columns[key][index]) for key in FORECAST_PARAMETERS},
            }
            for index, timestamp in enumerate(times)
        ]
        daily_records = [
            {
                "date": day,
                "values": {
                    key: _number(daily_columns[key][index])
                    for key in DAILY_FORECAST_PARAMETERS
                },
            }
            for index, day in enumerate(daily_times)
        ]
        units = payload["hourly_units"]
        daily_units = payload["daily_units"]
        if not isinstance(units, dict) or not isinstance(daily_units, dict):
            raise TypeError
    except WeatherProviderError as error:
        raise _provider_error(error) from error
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise HTTPException(status_code=502, detail="Open-Meteo returned an invalid hourly forecast.") from error

    return {
        "provider": "Open-Meteo",
        "source_url": "https://open-meteo.com/",
        "attribution": (
            "Weather data by Open-Meteo.com; API data CC BY 4.0. Values shown rounded to one decimal. "
            "Forecast model estimates, not observations."
        ),
        "data_kind": "forecast_model_estimate",
        "time_standard": "UTC",
        "latitude": latitude,
        "longitude": longitude,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "units": {key: units.get(key, FORECAST_UNITS[key]) for key in FORECAST_PARAMETERS},
        "daily_units": {
            key: daily_units.get(key, DAILY_FORECAST_UNITS[key])
            for key in DAILY_FORECAST_PARAMETERS
        },
        "records": records,
        "daily_records": daily_records,
        "cached_for_seconds": 10 * 60,
    }
