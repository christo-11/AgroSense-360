# AgroSense-360 Stage 23 Authorization Matrix

**Default:** NOT AUTHORIZED for every unconfirmed action

## Action authorization matrix

| Proposed action | Current status | Project-owner authorization | Source-owner permission | Required evidence | Responsible reviewer | Currently permitted? |
|---|---|---|---|---|---|---|
| Prepare draft inquiries | NOT AUTHORIZED | PO-01 | None to prepare, but terms must remain draft | Approved draft scope and owner list | Project owner/data governance reviewer | No |
| Send inquiries | NOT AUTHORIZED | PO-02 | Not permission to data use, but exact owner/channel must be verified | Message, recipient, geography, period, purposes and response destination | Project owner plus designated reviewer | No |
| Receive inquiries' responses | NOT AUTHORIZED | PO-03 | Not required for receipt if only reviewing, but response evidence may establish it | Secure response location and review process | Data governance reviewer | No |
| Store response evidence | NOT AUTHORIZED | PO-03 | Response may contain record-level restrictions | Original response, timestamp, sender, URL/location and integrity | Data governance reviewer | No |
| Download public datasets | NOT AUTHORIZED | PO-04 | Public licence and exact resource terms | Resource URL, exact version, licence, attribution, provenance and quality gate | Project owner, data engineer and governance reviewer | No |
| Acquire restricted datasets | NOT AUTHORIZED | PO-05 | Explicit written source-owner authorization | Scope, period, geography, permitted use, redistribution/training terms | Project owner and source/data reviewer | No |
| Use acquired data for portfolio/research | NOT AUTHORIZED | PO-06 | Exact research licence | Verified source, quality, provenance and Idukki/crop relevance | Research/data governance reviewer | No |
| Use data for research ML training | NOT AUTHORIZED | PO-07 | Explicit training permission | Signed approval, quality/relevance verification, immutable snapshot and provenance | Governance allowlisted reviewer | No |
| Use data for commercial ML training | NOT AUTHORIZED | PO-07 and PO-08 | Explicit commercial/training licence | Commercial rights, third-party clearance, signed approval | Project owner/legal reviewer/governance reviewer | No |
| Redistribute raw or processed data | NOT AUTHORIZED | PO-08 | Explicit redistribution permission | Licence/share-alike/third-party review and transformation terms | Legal/data governance reviewer | No |
| Create derived features or plots | NOT AUTHORIZED until data use is approved | PO-06 or later scope | Licence permits adaptation/derivatives | Source, formula/code version, provenance and attribution | Research/data engineer reviewer | No |
| Use existing ERA5-Land archives | NOT AUTHORIZED for acquisition/training; no new use approved | PO-06/PO-07 if proposed for any use | Copernicus and exact third-party terms | Existing manifest/quality/provenance and independent quality/validation | Data governance and scientific reviewer | No |
| Modify source inventory approval | NOT AUTHORIZED | PO-05/PO-06/PO-07/PO-08 as applicable | Source-owner permission plus governance approval | Evidence package and signed review | Governance allowlisted reviewer | No |
| Modify database/migrations/application behavior | NOT AUTHORIZED | Separate implementation authorization not granted | Data-use permission may be separate | Approved architecture/change scope | Project owner/technical owner | No |

## Cross-stage default decisions

The following remain unchanged from Stages 19–22:

- Idukki is **PROVISIONAL**.
- Existing ERA5-Land archives remain quality-rejected for training.
- No source is approved for training.
- No commercial source approval exists.
- No acquisition is currently authorized.
- No source-owner inquiry has been sent.
- No source-owner permission response is recorded.
