# DOST-ASTI EPDC manufacturing pre-screen

Checked 2026-10-30 (Asia/Manila). This is a read-only compatibility assessment of the DOST-ASTI EPDC documents supplied in `Documents/For PCB Ordering - DOST/` against the current active R2 PCB. It is not a quotation, manufacturing approval, order, fabrication release, or authorization to send files.

## Evidence and source identity

The supplied documents are local evidence, not instructions from the user to submit an order. The one-page Annex A attachment is labeled “Page 3 of 3”; the preceding process-flow pages are not present in the supplied file. The manufacturing-limit table on the supplied page was read directly:

| Source | Relevant content | SHA-256 |
|---|---|---|
| `Annex A Manufacturing Specs_EPDC-MAN-PM-001_rev 2.pdf` | Annex A, EPDC-MAN-PM-001 Rev 02 dated 2026-09-28, labeled page 3 of 3; PCB fabrication/assembly limits | `828CD4C70DF16A1F69586FF0DDFFFC977CEFB5BB4EDA86F3CBD4906106A3C2CC` |
| `DOST-ASTI-Citizens-Charter 2026.pdf` | EPDC intake/quote/job-order sequence on printed pp. 14-21; PCB price/lead-time bands and related services on pp. 31-32 | `586E6AC7133FC6511FE35A3901DFC22911673C8494FB3B8B6B21D4DEFC2EC26F` |
| `EPDC BROCHURE 2026.pdf` | General manufacturing capability summary, p. 2 | `92346FC2CEF505B95CEB8FAB9A9EA3317A9CC8A210FF81B7BFC2E7EEDD95C5D4` |
| `PCB-Manufacturing-and-Assembly-Inquiry-Form.pdf` | EPDC-SM-FM-002 Rev 2 dated 2025-06-13; one-page fabrication/assembly inquiry form | `80B85E11ACBAD77C1638163941951276571120F4E59DDB2ED46920F9AE876CD9` |

The active design was checked against `design/DESIGN_MANIFEST.json`. PCB SHA-256 `0EA352E982E6CCB87134D1D3DCEF7BD3ADB747EFAB5BA28B136CD1090F99540E`; project settings SHA-256 `3385C6421C31E40AC077A012399EF9AA61D7139E67994F81E040B26297A4D040`. The existing geometry report is `reports/engineering_audit/20261029/geometry.json`, SHA-256 `93659945D8895F4CCDB945070F34B1BF65C3F52A644BEC06DBD41146744AC4A2`.

The inquiry form PDF is a completed sample containing another client's personal/contact information and signature. `pypdf 6.10.0` reports no AcroForm fields. Do not return or modify this sample as the user's form; request a blank copy from EPDC or prepare a clean authorized copy from the official blank template. No third-party personal information is reproduced here.

## Capability limits stated in the attachments

The Rev 02 manufacturing sheet states: maximum outline 190 x 250 mm; FR4 only; 1.6 mm board thickness; 35 µm (1 oz) copper; 1- or 2-layer boards; minimum track/pattern width 0.30 mm; minimum pattern spacing 0.254 mm for 35 µm copper; minimum drilled hole 0.40 mm; minimum slotted-hole dimension 1.0 mm; minimum annular ring 0.254 mm; 0.30 mm minimum copper-to-board-edge distance; Gerber RS-274X input; bare-copper or immersion-tin finish; selected drill sizes listed from 0.4 mm through 2.0 mm and drill rounding to the nearest 0.1 mm. The sheet also describes through-hole plating as chemical-free organic conductive-polymer paste and says it is not recommended for high-current use.

For assembly, the same sheet lists consignment parts acquisition, polyimide stencils, 0201 minimum chip parts, SMT types except grid-array packages, radial/axial through-hole parts, IPC-A-610 as the reference standard, and lead-free solder/flux. Confirm exact assembly acceptance for the selected parts and process with EPDC.

## Active-board comparison

| Check | Current design evidence | Comparison to supplied EPDC sheet | Status |
|---|---|---|---|
| Layer count | KiCad reports 4 copper layers: F.Cu, In1.Cu, In2.Cu, B.Cu. The design uses inner ground-reference layers. | EPDC lists only 1 or 2 layers. | **Contradicted for fabrication as-is.** A 2-layer redesign would be a new electrical/layout candidate requiring its own return-path, USB, power, connectivity, ERC/DRC, and visual checks. |
| Outline | Manifest gives a 79.50 x 50.45 mm bounding box. | Each dimension is below 190 x 250 mm. | **Within the stated maximum by bounding dimensions.** Confirm final panel/outline interpretation with EPDC. |
| Board thickness | KiCad design setting is 1.6 mm. | EPDC specifies 1.6 mm only. | **Matches the nominal setting.** This is not yet a supplier-confirmed stackup. |
| Material and copper | No explicit stackup/material is recorded in the active board; engineering geometry report says `explicit_stackup_in_file: false`. | EPDC specifies FR4 and 35 µm (1 oz) copper. | **Unverified.** Obtain/confirm the actual EPDC stackup, copper basis, tolerances, and whether it supports the USB differential-impedance target. |
| Track width | KiCad 10.0.6 read-only board inspection: 599 copper track segments; 8 at 0.15 mm, 391 at 0.20 mm, 166 at 0.25 mm, with 34 segments at 0.40 mm or larger. | EPDC minimum is 0.30 mm. | **Contradicted as-is.** 565/599 segments (94.3%) are below the stated minimum. A full reroute/widening assessment is necessary. |
| Copper spacing | Active project minimum-clearance rule is 0.15 mm; engineering geometry report records representative long USB pair gaps of 0.153553 mm and 0.199999 mm. | EPDC minimum pattern space is 0.254 mm. | **Contradicted for those paths and the configured minimum.** Check all final copper geometry against the EPDC process after redesign. |
| Vias / holes | 99 vias have 0.60 mm copper diameter and 0.30 mm drill; nominal radial annular ring is 0.15 mm. | EPDC lists 0.40 mm minimum hole and 0.254 mm minimum annular ring. | **Contradicted as-is** if those minima apply to plated vias, as the table implies. Get EPDC confirmation of how its hole and annular-ring limits are applied to vias. |
| Larger mechanical holes | H1-H3 are 3.20 mm non-plated mounting holes. | The supplied drill-size table lists tools up to 2.0 mm. It does not expressly say whether larger drills or routed holes are unavailable. | **Open clarification.** Ask whether 3.20 mm NPTH holes are supported and at what tolerance/cost. Do not infer a hard maximum from the list alone. |
| Connector slots | USB-C shell pads use oval holes with a 0.60 mm minor dimension and 1.4/1.7 mm major dimensions. | EPDC lists 1.0 mm minimum slotted hole. | **Potential conflict.** Clarify whether the 1.0 mm minimum applies to slot width/minor dimension and whether the connector shell geometry can be fabricated. |
| Board-edge copper distance | Active project rule sets 0.50 mm minimum copper-edge clearance. | EPDC lists 0.30 mm minimum outside-route distance. | **Configured rule is nominally more conservative.** Recheck the final manufacturing outputs and their interpretation of routed outline. |
| Finish/colors | Current CAD does not select supplier finish or confirmed color availability. | EPDC offers bare copper or immersion tin and mask colors subject to availability; form checkboxes are a subset of the spec sheet's colors. | **Owner/supplier choice required.** Select with the quote; do not infer the mask color from a sample form. |
| High-current use | The board has a USB-powered 5 V input and regulator; no assembly measurement is present. | The sheet cautions that its stated through-hole plating process is not recommended for high-current applications. | **Unverified applicability.** Ask EPDC which PTH/via structures use this process and what current limits/derating apply; compare with measured and worst-case rail currents before approval. |
| Controlled impedance | No EPDC stackup or impedance coupon/calculation evidence is present in the supplied pack. Current board has no explicit stackup and includes USB differential routing. | The supplied capability documents state no controlled-impedance tolerance or stackup specification. | **Unverified; ask EPDC directly.** The omission is not proof that EPDC cannot provide it. |

## Intake form and service sequence

The provided form asks for client/billing/contact information; board name, dimensions, layer count, and quantity; silkscreen and mask colors; and, for assembly, board quantity, components per board/total, double-sided mounting, Gerber availability, component type, and BOM availability. It says to provide RS-274X Gerbers. The sample is already populated, so obtain a clean blank first.

The supplied 2026 Citizen's Charter says online clients start with an email inquiry to `epdc@asti.dost.gov.ph` (pp. 14-16); EPDC assesses the request and issues an official quotation (about two working days in the general EPDC workflow, p. 16); a signed quotation or equivalent document specifying amount and terms serves as the job order (p. 17); after service completion the client signs the work-completion notice and pays before release (pp. 18-21). The PCB-specific fee table is design/area/layer dependent and presents indicative lead-time hours (p. 31); do not treat those table values as a quote or guarantee. The provided form instead names `EPDC.SM@asti.dost.gov.ph` for the Gerber submission, while the charter and spec footer show `epdc@asti.dost.gov.ph`. Confirm the correct contact and exact initial-submission package with Bryle in the existing correspondence before sending design data.

These are the supplier's process instructions. The user's message provided the documents for review; it did not direct completion of the populated sample, generation of a manufacturing package, or submission to EPDC. No files were sent and no order was placed.

## Decision and next steps

**Recommendation:** Do not send the current 4-layer Gerbers as an order package to this 1-2-layer service. The active board also misses several stated geometry limits. First ask EPDC whether it can meet the electrical/mechanical constraints and confirm the ambiguous drill/via/plating details. If it cannot, obtain a quotation from a supplier that accepts the four-layer stackup and required geometries. If using EPDC, create a separately authorized 2-layer design candidate, then rerun electrical, geometry, manufacturing-rule, and physical acceptance planning against the confirmed process.

Before an eventual order, obtain: (1) a blank inquiry form; (2) confirmed layer count, stackup, copper, minimum geometry and hole treatment; (3) impedance support/stackup data for USB; (4) approval of high-current PTH/via use; (5) a formal quote, schedule, and payment/job-order terms; (6) correct Gerber/drill/BOM and assembly file requirements; and (7) user review of the complete package. User authorization is required immediately before an external submission or purchase.

## Review method and limits

- Text extraction: bundled Python 3.12.14, `pypdf` 6.10.0; PDF metadata/page counts and inquiry-form fields inspected.
- Visual inspection: Poppler 26.07.0 rendered Annex A p. 3, Citizen's Charter pp. 31-32, EPDC brochure p. 2, and the full one-page inquiry-form sample. Renders were stored in the system temp directory and were not added to the project.
- PCB source inspection: KiCad 10.0.6 `pcbnew` loaded the hash-matched active board read-only; inspected copper-layer count, thickness, track-width distribution, and via geometry. Project rule file and prior hash-linked engineering geometry report were compared.
- This is a document/CAD-geometry comparison, not vendor acceptance, Gerber validation, DFM, physical testing, a current quotation, or fabrication readiness. The Charter and supplied files were not independently confirmed online in this pass.

