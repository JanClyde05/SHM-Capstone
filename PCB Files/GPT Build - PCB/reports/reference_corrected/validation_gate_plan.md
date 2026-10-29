# Final corrected-candidate validation gates

Planned 2026-10-29 (Asia/Manila), before verifier changes. Scope: read-only CAD/source consistency checks in `tools/verify_corrected_board.py` and `tools/run_corrected_checks.py`. No circuit, routing, firmware, manuscript, or source requirements change.

## Proposed checks and acceptance

- Reject duplicate PCB/spec/XML references and unexpected PCB components; allow only the three documented board-only mounting holes H1–H3. Require matching spec/XML component sets and every XML endpoint's PCB pad.
- Verify the existing native USB pin contract explicitly (connector mirrored D+/D−, USBLC6 flow-through pins, R3/R4 and module pads 13/14) and require N16R8-reserved module pads 28–30 to remain unconnected. Sources: `docs/RESEARCH_LEDGER.md` SRC-02, SRC-03, SRC-07 and the current electrical definition. This is CAD net consistency, not USB compliance.
- Inspect actual MPU central-region pad and artwork geometry for copper/paste, independent of pad numbering. Require each documented die, antenna, and fastener rule area to exist, cover its intended geometry, span all four copper layers, and retain its prescribed exclusions. Sources: SRC-01 and the documented engineering placement plan. Ground planes remain permitted under the IMU die. This does not measure mechanical stress or assembly quality.
- Require both inner GND reference zones and four copper layers. Actual filled-plane continuity and return behavior remain subject to DRC/manual routing review; zone presence is not proof of signal integrity.
- Compare ERC/DRC ignored-check keys against the previously recorded KiCad 10.0.6 default sets. Reject newly suppressed check categories, unexpected explicit exclusions, incomplete severity coverage, missing report sections, or source changes during checks. Preserve all timestamped reports and hash the verifier scripts/project settings.

## Evidence boundary

Run Python syntax/help and bounded API-readiness checks before the final routed candidate exists. Final gate results may be claimed only after executing on the final candidate and retaining the hash-linked reports. CAD success does not establish controlled impedance, current capacity, physical assembly, thermal margin, sensor timing, or field frequency accuracy. Do not alter suppression settings to make a check pass.
