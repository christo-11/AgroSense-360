import tempfile
import zipfile
from pathlib import Path
from eccodes import codes_grib_new_from_file, codes_get, codes_release

archive = Path("data/raw/weather/era5_land/era5_land_request_2.zip")
targets = ("tvh.grib", "tvl.grib")

with tempfile.TemporaryDirectory(prefix="era5_grib_check_") as temp_dir:
    with zipfile.ZipFile(archive, "r") as zf:
        for target in targets:
            matches = [
                name for name in zf.namelist()
                if name.lower().endswith(target)
            ]

            print(f"\n===== {target} =====")

            if not matches:
                print("ERROR: Member not found")
                continue

            for member in matches:
                info = zf.getinfo(member)
                extracted_path = Path(
                    zf.extract(member, path=temp_dir)
                )

                message_count = 0
                total_message_bytes = 0

                with extracted_path.open("rb") as stream:
                    while True:
                        gid = codes_grib_new_from_file(stream)

                        if gid is None:
                            break

                        try:
                            length = int(codes_get(gid, "totalLength"))
                            edition = int(codes_get(gid, "edition"))

                            message_count += 1
                            total_message_bytes += length

                            print(
                                f"Message {message_count}: "
                                f"edition={edition}, totalLength={length}"
                            )
                        finally:
                            codes_release(gid)

                difference = info.file_size - total_message_bytes

                print(f"Member: {member}")
                print(f"ZIP uncompressed member size: {info.file_size}")
                print(f"Messages parsed: {message_count}")
                print(f"Sum of message lengths: {total_message_bytes}")
                print(f"Difference: {difference}")
                print(
                    "All message lengths match member size: "
                    f"{total_message_bytes == info.file_size}"
                )
