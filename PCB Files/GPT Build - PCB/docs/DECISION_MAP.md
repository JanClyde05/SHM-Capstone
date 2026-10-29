# Requirements, design decisions and unresolved details

Updated 2026-10-28. The user's reference correction supersedes the earlier larger-outline choice. This map separates direct requirements, observed file facts, design choices and unresolved evidence. Manufacturer-source verification and actual CAD results are recorded in their dedicated logs.

| ID | Item | Basis/status | Required evidence or consequence |
| --- | --- | --- | --- |
| REQ-01 | ESP32-S3-WROOM-1-N16R8 | Explicit user choice | Correct module pin/land pattern; preserve PSRAM pins35/36/37 |
| REQ-02 | Three bare MPU-6050 on one board | Explicit user choice | Each IC needs its complete manufacturer support circuit; no breakout assumptions |
| REQ-03 | USB-C external power and programming | Explicit user choice | Native USB GPIO19/20, sink CC termination, protection and verified power budget |
| REQ-04 | Retain similar old board/schematic aesthetic where practical | Explicit user preference, flexible | Preserve rounded three-lobe form and orderly repeated sensor blocks; engineering clearance has priority |
| REQ-05 | Firmware correlation | Current source inspection | Bus0 GPIO8/9; bus1 GPIO10/11; INT4/5/6; AD0 low/high/low |
| REQ-06 | One fixed roadway-deck station, separate XYZ streams | Approved research scope | All three devices aligned and rigidly supported; no spatial mode-shape or synchronized-clock claim |
| REQ-07 | Only `Thesis/SHM_PCB_New/` is the intended old reference | Verified user correction2026-10-28 | Use root `SHM_PCB_New.kicad_sch/.kicad_pcb`; parent Thesis and nested prototype are historical alternatives |
| DES-01 | Larger original Thesis outline | **Superseded; contradicts clarified reference** | Old choice approx83.6 x83.1mm including stroke; preserve provenance, replace as active geometry basis |
| DES-05 | Compact `SHM_PCB_New` outline | Verified file geometry, required correction basis |79.50 x50.45mm centerline;12 edges; repeat placements/clearances/routing checks on corrected output |
| DES-02 | Four copper layers | Integration design choice | Select stackup and return planes; impedance cannot be asserted from trace width alone |
| DES-03 | New circuit and routing | Required by current firmware and old defects | Do not reuse old AD0 switching, unconnected INT or obsolete power assumptions |
| DES-04 | Native KiCad10.0.6 artifacts and generator scripts | Installed tooling / reproducibility choice | Keep generated files editable; do not overwrite later manual edits silently |
| OPEN-01 | Exact PCB manufacturer and stackup | Not user-confirmed | Record selected dielectric/copper construction before any controlled-impedance fabrication claim |
| OPEN-02 | Enclosure and mounting interface | Not user-confirmed | PCB can provide proposed mounting holes, but mechanical fit to an external enclosure remains unverified |
| OPEN-03 | Exact connector and supporting-component purchase variants | Requires verified selection | Check manufacturer drawings/ratings and mark proposed MPNs as proposed until sourcing is confirmed |
| OPEN-04 | Power source/cable capability and USB host conditions | No physical evidence supplied | Define operating source requirement and measure actual device behavior |
| OPEN-05 | Thermal margin and supply transients | Calculations plus later prototype evidence needed | Regulator current rating alone is insufficient; record dissipation/area/ambient assumptions |
| OPEN-06 | CAD connectivity/clearance compliance of corrected board | Unverified until correction rechecks | MD14's zero-active-violation result applies to old larger-outline hashes only; rerun ERC/DRC/net/geometry/visual review after correction |
| OPEN-07 | Sensor noise, clock timing and frequency accuracy | Hardware not measured here | Preserve bench verification plan; do not infer accuracy from mathematical software checks |

Existing old sources remain reference-only. Manufacturer values must be logged with citations; local choices such as board size, test-point arrangement and mounting-hole layout must be described as choices with their reasons. New assumptions should be added explicitly to this table or the completed design report.
