# V5 figure and layout assets

These files support the separate V5 review candidate. They do not replace the active KiCad design, certify field performance, or change V2's approval status.

## Figure sources

- `create_v5_flowcharts.py` generates the monochrome Figure 3.4 firmware flow and Figure 3.5 field-collection workflow as SVG and PNG with Inkscape 1.4.2.
- `build_v5_candidate.py` starts from V4, writes a separate V5 DOCX, applies the logged abstract/glossary layout, centers all figure/caption pairs, updates the Figure 3.4 List of Figures label, and replaces only the embedded Figure 3.4 and 3.5 raster images.
- `../verification/verify_v5_layout.py` checks the DOCX package, glossary emphasis, seven captioned figure pairs, image color/placeholder properties, printed page map, and static lists. Its machine-readable result is `../verification/v5_layout_verification_20261029.json`.

Run from the project root with the workspace Python 3.12 runtime:

```powershell
& 'C:\Users\Jan Clyde Talosig\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'MD Files\figures_v5\create_v5_flowcharts.py'
& 'C:\Users\Jan Clyde Talosig\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'MD Files\figures_v5\build_v5_candidate.py'
```

Then export the V5 DOCX with Microsoft Word and run the V5 verifier. The output paths and acceptance checks are fixed in those scripts. Preserve the V4 DOCX/PDF as source snapshots; the builder writes only the V5 paths.

## Visual rules preserved

Figures 1.1, 3.1, 3.4, and 3.5 are monochrome. Figure 1.2 preserves the colored bridge map from V4. Figures 3.2 and 3.3 remain blank white frames with black borders. Schematic and PCB design files were not edited. Figure 3.4 depicts current firmware behavior; Figure 3.5 depicts the proposed field workflow and is not evidence that permissions or approvals have been obtained.

## Review limitations

The figures and layout were visually inspected in Word-exported PDF pages. This is not a full-text reference audit, ethics/privacy decision, Turnitin result, AI-writing review, firmware build, CAD validation, hardware test, or field validation. The manuscript/firmware window-selection and valid-window conflicts remain open in the project ledgers.
