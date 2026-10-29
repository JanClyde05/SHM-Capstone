# Prototype operation and research recording

Updated 2026-10-24. The integrated Arduino sketch compiles; the physical prototype and research measurements remain unverified. Read `ARDUINO_IDE_SETUP.md`, `HARDWARE_INTERFACE.md`, and `MATHEMATICAL_ALGORITHMS.md` before the first run. The sequence below uses the implemented operator controls and PC tools.

## 1. Wire and flash

1. Check the exact carrier against the proposed map in `hardware_profile.h`: bus 0 GPIO8/9 with IMU1 `0x68` and IMU2 `0x69`; bus 1 GPIO10/11 with IMU3 `0x68`; three separate INT lines to GPIO4/5/6. Check bare-IC supply, logic voltage, pull-ups, decoupling, AD0 and orientation before power. Inspect the native USB wiring and reserve GPIO19/20.
2. Open `firmware/SHM_Capstone/SHM_Capstone.ino` in Arduino IDE. Use **ESP32S3 Dev Module**, **QIO 80MHz**, **16MB flash**, **OPI PSRAM**, **Custom** partition, and native USB CDC settings in the setup guide. Compile and upload. The embedded dashboard is included; no LittleFS web-asset upload is needed.
3. Open Serial Monitor at **115200**, with a newline line ending. Record firmware version, board/core configuration and prototype wiring. Keep power on through any capture and persistence phase.

## 2. Initialize and connect

If LittleFS does not mount on a new/blank device, explicitly send:

```text
FORMAT_ERASE_ALL
```

This erases the measurement filesystem. Use it only for deliberate initialization or after backing up all retained recordings. Mount errors never trigger automatic formatting. A second firmware upload normally preserves existing files when the partition map is unchanged and **Erase All Flash Before Sketch Upload** is disabled.

Serial output supplies the **SHM-…** access-point name, password and dashboard URL. Record the password privately during the first bench setup. Firmware generates it once and retains it in NVS (`shm-network` / `ap-pass`); ordinary power cycles and uploads preserving NVS retain it, so a USB host is unnecessary for later external-supply boots. `FORMAT_ERASE_ALL` formats LittleFS and retains the network password. A whole-flash erase clears it, campaign settings and recordings; record the newly generated password after such maintenance. Credentials are printed only to Serial, not exposed through the web API or measurement files.

Join that network, keep the local connection when the phone reports no internet, and open the printed address. If NVS persistence cannot be verified, the AP does not start; inspect the Serial diagnostic. Load the dashboard before starting a recording; full-page assets and downloads are blocked during active capture/processing.

Confirm the dashboard reports hardware, PSRAM and storage ready. Run the **ten-second precheck**. A rejected check requires investigation of sensor identity/configuration, INT wiring, data continuity, clipping or timing. A precheck pass is a short acquisition check; it does not establish calibrated vibration accuracy or verify a whole field session.

## 3. Collect pilot sessions

Enter a consistent **station ID**, explicit **board orientation**, operator and observation notes. Use the approved roadway-deck station, authorized mounting and a documented visual counting point. Do not invent bridge coordinates or mounting details in metadata.

Select **pilot**, run a fresh precheck if needed, and start. The device resets/wakes the sensors and displays a **five-second countdown**. Begin the visual traffic tally when the **600-second recording interval** begins. Count vehicles passing the same declared reference line/directions throughout that interval. Stop the tally when the interval ends. Keep the count on a field sheet as well as entering it into the dashboard; this preserves the observation if the browser disconnects.

Record for the full interval; do not stop when a desired count is reached or extend a low-traffic recording. **ABORT CAPTURE** retains an incomplete session and excludes it from the formal baseline. After normal capture, wait through **PROCESSING** until the recording is stored and the device requests the vehicle tally. Enter that session ID and observed integer count, then finalize it.

Data remain in PSRAM during capture. The maximum raw buffer is 6.4 MB, and nominal raw payload is about 5.76 MB per session. Flash persistence occurs afterward while acquisition is suspended. A power loss/reset before successful persistence can lose the interval. Keep power on until persistence completes, then export the files.

## 4. Export and independently reproduce

Download **raw**, **windows**, and **summary** for every completed session. Keep their common session ID in the filenames. Raw downloads use SHMRAW2 binary records with `.shmb` extension; the decoder accepts that extension. Store field notes and the observed tally beside those files.

From a PC with Python 3 and NumPy, change to the project's `tools` directory. For a session saved as `S123_raw.shmb`, `S123_windows.csv`, and `S123_summary.json`, run:

```powershell
python analyze_session.py S123_raw.shmb --summary S123_summary.json --windows S123_windows.csv --output S123_offline.json
```

Supply the files' full paths if they are elsewhere. Inspect CRC, timing/continuity, clipping, valid-window counts, peak bins, frequencies and any firmware/reference differences. Preserve the offline output. Investigate discrepancies before using a session in the research analysis. The mathematical audit map explains exactly what each check establishes.

## 5. Derive actual traffic cutoffs and freeze

Gather complete pilot count intervals spanning the local traffic conditions. Supply all eligible pilot summaries from the same station/orientation to:

```powershell
python derive_traffic_cutoffs.py --output pilot_cutoffs.json S1_summary.json S2_summary.json S3_summary.json S4_summary.json S5_summary.json S6_summary.json
```

Replace those example filenames with actual pilot files. This command has no invented vehicle thresholds. It sorts actual ten-minute counts and derives nearest-rank empirical tertiles: `c1 = C_(ceil(m/3))`, `c2 = C_(ceil(2m/3))`. If ties collapse thresholds or leave a group empty, extend/revise the pilot before freezing. The optional `--require-technical-valid` additionally requires accepted vibration QC; without it, complete traffic-count intervals can contribute while rejected device QC remains explicitly recorded. See `tools/README.md`.

Review the pilot evidence for frequency band and timing tolerance as well. Enter the resulting **cutoff1/cutoff2**, station, orientation and analysis settings into the dashboard freeze form and confirm **FREEZE**. Preserve `pilot_cutoffs.json`, the pilot inputs and the displayed configuration hash. Classification thereafter is `C ≤ c1` → NEAR_ZERO, `c1 < C ≤ c2` → MEDIUM, and `C > c2` → HEAVY. NEAR_ZERO can contain a nonzero count.

## 6. Formal sessions and baseline

Use **formal** mode after freezing; station/orientation must match. Run precheck again and repeat the same five-second countdown, 600-second acquisition/tally, persistence, finalization and export procedure. Group membership comes from the final concurrent count and frozen cutoffs. Pilot observations do not enter the formal baseline.

The current firmware uses these **provisional engineering settings**, requiring prototype/pilot evaluation:

| Setting | Current value and meaning |
| --- | --- |
| Sensor rate | Nominal 100 Hz per IC, accepted measured rate within ±3% |
| Interval timing residual | At most 500 µs from the measured mean sample period by default |
| Analysis windows | Ten nonoverlapping 60-second windows; all ten required per channel/axis session median |
| Clipping threshold | Absolute raw count at least 32000 flags near-rail input |
| Initial analysis band | 0.5–20 Hz, subject to pilot evidence and sensor response |
| Baseline target | At least five accepted formal session values per group/channel/axis |

These values are not empirical performance results, calibrated accuracy limits or a statistical power calculation. Freeze justified settings before formal collection. The mean ± sample SD band describes observed spread; the separate mean ± 2 SD band is a review heuristic. Neither establishes bridge condition or a formal 95% interval.

## 7. Retention, pending tallies and maintenance

Back up all three exported files and the offline reproduction before reclaiming space. To remove only a backed-up raw file while keeping its summary/window data, send the exact session ID through Serial Monitor, for example:

```text
PURGE_RAW S123 CONFIRM
```

Use your actual ID. The 16 MB flash cannot hold the whole planned campaign's raw data. A new session is rejected when reserve is insufficient; it never automatically deletes old recordings. Keep the external raw backup because a retained summary alone cannot reproduce its frequency estimates.

If the device rebooted **after files were successfully stored but before the tally was finalized**, open its retained session list. Use the count-finalization form with that stored session ID and the original field-sheet count. The implemented recovery reads that summary's saved settings/cutoffs; it does not substitute today's configuration. Download the updated summary afterward. Already-finalized summaries are not silently overwritten. A reboot during the PSRAM capture or an incomplete flash write cannot be repaired by entering a count.

For formal campaign statistics, supply independently reproduced session outputs to `analyze_campaign.py` as documented in `tools/README.md`. Archive accepted and rejected observations with their QC reasons. Record actual prototype outcomes in the reports and handoff before the planned Astra mathematical audit/KiCad work and subsequent reviewed-design BOM task.
