import zipfile
from pathlib import Path

archive = Path("data/raw/weather/era5_land/era5_land_request_2.zip")

with zipfile.ZipFile(archive, "r") as zf:
    for target in ("tvh.grib", "tvl.grib"):
        matches = [
            name for name in zf.namelist()
            if name.lower().endswith(target)
        ]

        print(f"\n===== {target} =====")

        if not matches:
            print("ERROR: Member not found")
            continue

        for member in matches:
            data = zf.read(member)
            declared = int.from_bytes(data[4:7], "big")

            print(f"Member: {member}")
            print(f"Declared boundary offset: {declared}")
            print(f"Bytes at declared boundary: {data[declared:declared+4]!r}")
            print(f"Bytes at actual end: {data[-4:]!r}")
            print(f"Remaining bytes after declared boundary: {len(data)-declared}")
            print(f"GRIB signatures in member: {data.count(b'GRIB')}")
            print(f"7777 markers in member: {data.count(b'7777')}")
