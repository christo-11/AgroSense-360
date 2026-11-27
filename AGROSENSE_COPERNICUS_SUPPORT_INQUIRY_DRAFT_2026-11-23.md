# Copernicus CDS Support Inquiry Draft

**Status:** Draft for review only; not sent

**To:** Copernicus Climate Data Store Support Team  
**Subject:** Technical clarification requested: ERA5-Land GRIB1 header-length inconsistency

Dear Copernicus Climate Data Store Support Team,

We are reviewing an existing ERA5-Land GRIB download and would appreciate technical clarification about two ancillary GRIB1 members.

The members `tvh.grib` and `tvl.grib` are contained in:

`data/raw/weather/era5_land/era5_land_request_2.zip`

The archive corresponds by content to the recorded ERA5-Land request with manifest reference `7aa7a686527d3e900aa7b8dce4709fa6`. The related historical receipt is recorded as UUID `4e1e2a12-1800-4983-80ea-4ab38a1fd5f4`; the project's reconciliation notes that this receipt-to-archive association is based on matching request details, not a direct identifier-level mapping.

For each member, raw inspection found:

- GRIB edition 1, with initial bytes `47 52 49 42 81 A6 1D 01`.
- The three-byte header length `81 A6 1D` declares **8,496,669 bytes**.
- The actual uncompressed ZIP-member size is **12,967,284 bytes**, a difference of **4,470,615 bytes**.
- Each member contains one GRIB signature and one `7777` end marker and ends with `7777`.
- The four bytes at the declared boundary are `00 00 98 00` for `tvh.grib` and `08 00 08 00` for `tvl.grib`.
- ecCodes parses one message per member and reports **12,967,284 bytes** for each.

The ZIP archive passed its recorded integrity checks, while the internal GRIB1 length discrepancy remains unresolved. We are not asserting that the files are corrupt and have not altered them.

Could your technical team please confirm:

1. Is this header-length discrepancy expected for these ERA5-Land GRIB1 members?
2. Are these files valid and conformant with the expected GRIB1 encoding?
3. Is there a known encoding, packaging or processing issue that explains the discrepancy?
4. Are corrected versions of these files available?
5. Should users avoid relying on these members until clarification is provided?

We would appreciate a technical response and, if applicable, corrected source files or the appropriate official procedure for obtaining them.

Thank you for your assistance.

Regards,  
AgroSense-360 project team

---

**Internal handling note:** This is an unsent draft. No support team has been contacted, and this draft does not grant authorization to send an inquiry, acquire corrected files, or use the affected members for research, redistribution, commercial purposes or ML training.
