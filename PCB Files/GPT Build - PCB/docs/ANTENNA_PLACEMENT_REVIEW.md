# Antenna overhang and compact-reference review

Checked2026-10-29. Status: **verified** source guidance and old CAD coordinates; **partially verified** placement inference; **unverified** final corrected layout, enclosure and RF performance. No CAD file was changed by this review.

## Primary sources

- Espressif [ESP32-S3 Hardware Design Guidelines, module positioning](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html#general-principles-of-pcb-layout-for-modules-positioning-a-module-on-a-base-board), opened2026-10-29. It recommends antenna overhang with the feed point near the base-board edge. If overhang is impossible, it advises base-board cutouts beside and beneath the antenna. It separately recommends at least15mm clearance around the antenna inside the final housing and final-product range/throughput testing. These are layout recommendations, not proof of this board's RF performance.
- Espressif [ESP32-S3-WROOM-1/WROOM-1U datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), opened2026-10-29, §11.1 Figure11-1 printedp45 and §11.2 printedp46. The module-specific drawing identifies the antenna region and recommended land pattern; §11.2 directs base-board positioning to the hardware guidelines. Apply module guidance to this complete WROOM assembly; bare-chip RF matching guidance is not a requirement to duplicate its internal circuit.

## Directly observed old CAD facts

Source: `../Reference PCB (OLD Version)/Thesis/SHM_PCB_New/SHM_PCB_New.kicad_pcb` relative to hardware root. SHA-256:`372996943A9C3EB3C9087C315B7C810DF9C0B70A4E0D1B47A99E9EC81B52C23F`. Read using installedKiCad10 pcbnew, without saving.

| Item | Observed value |
| --- | --- |
| Exact outline centerline limits | X99.15..178.65, Y53.55..104.00mm |
| Exact outline centerline size |79.50 x50.45mm; not69mm |
| Old module origin/rotation | (138.90,60.55),0degrees |
| Module F.Fab exterior | X129.90..147.90, Y47.80..73.30mm |
| Footprint antenna/body boundary | Horizontal lineY53.80mm, localY−6.75mm |
| Straight top board edge beneath module | Y53.55mm |
| Footprint antenna rule-area bounds | X114.90..162.90, Y32.80..53.80mm |
| Pad1/40 centers and sizes | (130.15,55.29)/(147.65,55.29),1.50 x0.90mm |

## Interpretation and proposed correction

The footprint-defined antenna region extends0.25mm beyond the board-edge line toward the interior:53.80−53.55=0.25mm. This is a CAD geometric observation, not a measured feed-point coordinate or RF loss. Reusing the old placement exactly therefore does not demonstrate full antenna overhang.

For this footprint at0degrees, requiring the antenna/body boundary to lie on or outside the top edge gives `module_origin_Y − 6.75 ≤ 53.55`, hence `module_origin_Y ≤ 60.30mm`. A candidateY60.20 gives0.10mm nominal separation. Root must select the actual position using the authoritative module drawing, actual footprint and board/assembly tolerances; this small nominal gap is not a tolerance analysis. Recheck the first side-pad edge, module ground lands, all-layer antenna keepout and nearby hardware. Do not use this simple boundary calculation as evidence that the antenna feed point itself was located exactly.

The15mm enclosure recommendation should be recorded as an external assembly constraint. It does not justify clearing all copper beneath the shielded module body or every module pin. Antenna exclusion and ground continuity beneath the remaining module body are separate layout concerns. Actual range/throughput with the intended enclosure, mounting metal and bridge placement remains unmeasured.

## Closure evidence

Save final module origin/rotation and boundary calculations; verify the actual antenna/baseboard intersection and layer keepouts; inspect assembly overhang and mounting clearances; identify enclosure/material/metal placement; then record powered end-product communication measurements. Repeat the CAD checks after a placement change. Current source/report hashes must distinguish corrected compact R2 from the earlier larger-outline board.

Tool note: the first read-only zone query used unavailable `GetRuleArea`; rerunning withKiCad10 `GetIsRuleArea` returned the bounds above. No failed API result was used as geometric evidence.
