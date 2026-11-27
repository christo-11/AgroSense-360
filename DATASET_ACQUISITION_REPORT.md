# ERA5-Land Acquisition and Inspection Report

## Result

Both supplied Copernicus object-store results were downloaded, validated, and inspected. This report records that historical acquisition and its technical validation; it does not establish that acquisition was authorized or grant permission for subsequent project activity. Published availability, object URLs, and publisher licence/terms do not substitute for project-owner authorization or applicable source-owner permission. The URLs were used in the order supplied; the actual sizes are opposite the user-reported estimates. The request-history MHT was not independently inspected, so the successful status in the manifest is recorded as user-reported. Exact request selections cannot be confirmed from the object URLs alone.

| Request reference | Local archive | Actual size | SHA-256 | ZIP / CRC |
|---|---|---:|---|---|
| `24a5f33e75200171321741639baf695f` | `data/raw/weather/era5_land/era5_land_request_1.zip` | 647,003,080 bytes (617.03 MiB) | `337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441` | Passed / passed |
| `7aa7a686527d3e900aa7b8dce4709fa6` | `data/raw/weather/era5_land/era5_land_request_2.zip` | 2,026,384,498 bytes (1,932.51 MiB) | `dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0` | Passed / passed |

Both server `Content-Length` values matched the downloaded file sizes. The two archives were not overwritten, extracted, or preprocessed. The raw-data directory is Git-ignored.

## Archive contents

**Request 1 (NetCDF)** contains `data_0.nc`, `cicecap.nc`, `clake.nc`, `cvh.nc`, `cvl.nc`, `dl.nc`, `geo.nc`, `lsm.nc`, `slt.nc`, `tvh.nc`, and `tvl.nc`.

**Request 2 (GRIB)** contains `data.grib`, `cicecap.grib`, `clake.grib`, `cvh.grib`, `cvl.grib`, `dl.grib`, `lsm.grib`, `slt.grib`, `tvh.grib`, and `tvl.grib`. The main `data.grib` member is 3,672,867,984 bytes uncompressed. The full member names and sizes are in the provenance manifest.

## Observed weather data

Both archives cover the entire globe (`-90` to `90` latitude and `0` to `359.9` longitude), so their grids include Kerala. Observed latitude/longitude spacing is 0.1 degrees. Request 1 identifies CF-1.7 latitude and longitude coordinates in degrees north/east; request 2 uses a `regular_ll` grid. Neither contains a separate CRS declaration.

### Request 1

`data_0.nc` is NetCDF-4/HDF5 from ECMWF and declares CF-1.7 conventions. Its two `valid_time` coordinates are **2024-01-03 03:00 and 06:00 UTC**, giving a three-hour observed interval, not a continuous hourly series. Its 37 data variables and units include:

- Temperature: `t2m`, `lblt`, `lict`, `lmlt`, `ltlt`, `tsn` (K)
- Soil water: `swvl1`-`swvl4` (m^3 m^-3)
- Precipitation and water fluxes: `tp`, `pev`, `ro`, `sro`, `ssro` (m); `e`, `es`, `evabs`, `evaow`, `evatc`, `evavt`, `sd`, `sf`, `smlt`, `src` (water-equivalent metres)
- Wind: `u10`, `v10` (m s^-1); surface pressure: `sp` (Pa)
- Other snow, lake, vegetation, and albedo variables: `asn`, `lai_hv`, `lai_lv`, `licd`, `lmld`, `lshf`, `rsn`, `sde`, `snowc`

The other NetCDF members contain ancillary fields: glacier mask `glm`, lake cover/depth `cl`/`dl`, high/low vegetation cover `cvh`/`cvl`, geopotential `z`, land-sea mask `lsm`, soil type `slt`, and high/low vegetation type `tvh`/`tvl`. Their single coordinate timestamps are ancillary metadata, not a continuous historical weather series.

NetCDF `_FillValue`/`missing_value` attributes were recorded (including NaN and `-32767` markers where present). Per-cell missing-value counts were not computed because the data arrays were not scanned.

### Request 2

ecCodes inspected **609 GRIB messages** (editions 1 and 2). Fifty variables have 12 distinct timestamps each, spanning **2011-01-11 13:00 to 2011-01-29 22:00 UTC**. The observed gaps are irregular (2, 7, 15, 63, and 327 hours); these files are not a continuous hourly time series. The manifest contains each variable's own date coverage and observed intervals.

The time-varying variables include temperature (`2d`, `2t`, `skt`, `stl1`-`stl4`, K), soil water (`swvl1`-`swvl4`, m^3 m^-3), precipitation/runoff/evaporation, 10-m wind (`10u`, `10v`, m s^-1), pressure (`sp`, Pa), and snow, radiation, lake, and vegetation fields. The nine remaining variables are single-timestamp ancillary fields. Although all GRIB validity timestamps span 1995-2025 when those ancillary records are included, that is **not** the temporal coverage of the time-varying series.

The GRIB missing-value marker is `9999`; ecCodes reports 0 to 4,270,737 missing points per message. The grid type is `regular_ll`, with 0.1-degree latitude/longitude increments.

**Format limitation:** the `tvh.grib` and `tvl.grib` members declare a GRIB message length of 8,496,669 bytes, while each member is 12,967,284 bytes. ecCodes successfully parsed each complete member, and ZIP CRC checks passed, but the internal length mismatch is retained in the manifest and should be checked before relying on those two ancillary fields.

## Suitability and limitations

The archives contain variables technically relevant to weather-data analysis, including temperature, precipitation, wind, pressure, and soil moisture, and their global grids include Kerala. This technical relevance does not authorize access, acquisition, research, portfolio/public demonstration, training, redistribution, or deployment. The Stage 12D inventory classification records only apparent publisher licence/terms compatibility; it is not project-owner authorization or source-owner permission. Current project use scopes remain **NOT AUTHORIZED**. The archives are reanalysis/model estimates rather than direct local observations. These request results are sparse samples, not a continuous hourly or Kerala-specific time series, and are not sufficient by themselves for production weather features or seasonal analysis. Commercial use remains a separate assessment.

## Provenance and licence

The manifest records the official ERA5-Land dataset page, the Copernicus Licence to Use Copernicus Products v1.2 (November 2019), attribution/disclaimer language, and the third-party-data exception. Attribution recorded there is:

> Generated using Copernicus Climate Change Service information [Year]. For adapted or modified material: Contains modified Copernicus Climate Change Service information [Year]. Neither the European Commission nor ECMWF is responsible for any use that may be made of the information.

The exact request parameters could not be independently recovered because the MHT history file was unavailable in this run. The downloaded files were inspected directly; no variables, dates, or bounds were inferred from the request descriptions.

## Files and validation

- Downloader: `backend/scripts/download_era5_requests.py`
- Provenance manifest: `data/metadata/era5_land_download_manifest.json`
- Raw archives: `data/raw/weather/era5_land/era5_land_request_1.zip` and `data/raw/weather/era5_land/era5_land_request_2.zip`

Both downloads passed size, ZIP-format, and ZIP CRC validation. SHA-256 values and complete member inventories are recorded above and in the manifest. No application, database, `.env`, or `.cdsapirc` files were changed. No dataset extraction, preprocessing, or model training was performed.
