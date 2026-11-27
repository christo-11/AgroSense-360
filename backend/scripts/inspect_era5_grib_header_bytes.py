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

            print(f"Member: {member}")
            print(f"Uncompressed size: {len(data)}")
            print(f"First 16 bytes (hex): {data[:16].hex(' ')}")
            print(f"GRIB signature: {data[:4]!r}")
            print(f"Edition byte: {data[7:8].hex()}")

            if data[:4] == b"GRIB" and data[7] == 1:
                header_length = int.from_bytes(data[4:7], "big")
                print(f"GRIB1 header length from bytes 5-7: {header_length}")
                print(f"ecCodes-reported length from previous test: 12967284")
                print(f"Header length equals member size: {header_length == len(data)}")
            else:
                print("Unexpected signature or edition; do not interpret as GRIB1.")

            print(f"Final 4 bytes: {data[-4:]!r}")
