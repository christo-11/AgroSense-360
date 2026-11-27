# AgroSense-360 Stage 26 — Owner Review and Submission Checklist

**Date:** 23 November 2026  
**Current status:** **AWAITING PROJECT-OWNER REVIEW**  
**Submission status:** **NOT SENT**  
**External response:** **NOT RECEIVED**  
**External permission:** **NOT GRANTED**  
**Stage 23 restrictions:** **UNCHANGED**

This checklist is for owner review of the existing Copernicus CDS technical clarification inquiry only. It does not record owner approval, authorize submission, or authorize acquisition or use of data.

## Review findings

The draft is concise, professional, and clear about asking for technical clarification. It identifies the affected request 2 archive and members, reports the header-length discrepancy without asserting that the files are corrupt, and asks whether the format is expected/conformant, whether a known processing issue explains it, whether corrected files are available, and whether users should rely on the members pending clarification. The receipt UUID is distinguished from the manifest request reference; their direct identifier-level mapping is not established.

The reported measurements agree with the technical evidence report and diagnostic addendum: both members declare 8,496,669 bytes, each has an actual uncompressed size of 12,967,284 bytes, and the difference is 4,470,615 bytes. Both end with `7777`; the reported boundary bytes differ by member, and ecCodes reports one message of 12,967,284 bytes for each. The cause remains unknown.

The evidence report records these archive checksum matches:

| Archive | Request reference | SHA-256 |
|---|---|---|
| `era5_land_request_1.zip` | `24a5f33e75200171321741639baf695f` | `337a03f81662103ad43cf063a885162c8f6c920e44f16c9ead6d8dff09539441` |
| `era5_land_request_2.zip` | `7aa7a686527d3e900aa7b8dce4709fa6` | `dec4dc9b22c17208a8e9b1ea6d945662a20b3d1433347a6b044006dca44529f0` |

The inquiry concerns request 2. Including its checksum in the submitted evidence package will help identify the exact archive; request 1's checksum is only a comparison record.

## Project-owner checklist

Before any submission, the project owner should:

- [ ] Review the inquiry wording and confirm the technical claims, member names, byte counts, request reference, and receipt-identifier caveat are clear and accurate.
- [ ] Confirm the inquiry does not overstate the evidence: the discrepancy is observed, but its cause and whether it is an encoding or processing issue are unknown.
- [ ] Attach the technical evidence report and diagnostic addendum; include the request 2 archive SHA-256 and relevant existing manifest/quality evidence where appropriate.
- [ ] Verify the recipient and submission method through the official Copernicus CDS support channel. No contact address or endpoint was verified in the reviewed files.
- [ ] Give explicit approval for the final inquiry and its attachments to be submitted. Owner review alone is not submission authorization.
- [ ] If approval is given later, verify the approved version and attachments immediately before sending.

Do not attach the full archive by default. Share it only if the owner separately authorizes sharing and the verified official channel requests it.

## Authorization boundary

No inquiry has been sent, no response has been received, and no external permission has been granted. A CC-BY licence must not be interpreted as owner approval to contact Copernicus or as permission for research, pilot, commercial use, redistribution, or ML training. None of those uses is authorized by this checklist. Existing Stage 23 restrictions remain unchanged.

## Decision

**Awaiting project-owner review.** Submission may be considered only after the owner completes the checklist and explicitly approves sending the reviewed inquiry through a verified official support channel.
