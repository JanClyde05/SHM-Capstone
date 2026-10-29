# Firmware prototype report - 2026-10-24

## Delivered scope

[Certain] Implemented Arduino IDE prototype firmware in firmware/SHM_Capstone for the user-confirmed ESP32-S3-WROOM-1-N16R8 and three MPU6050 ICs. Paper v2 was approved; DOCX files, original program, source MD Files and old KiCad files were not edited in this firmware turn. GPT Paper MD files received approval-status updates only.

[Certain] The build contains separate acquisition, MPU register/FIFO, session, pure DSP/statistics, storage, timing, AP and embedded-HTTP UI modules. The active dashboard follows the user's global dark zinc UI. Old data/ assets remain explicitly inactive. There is no PlatformIO project or required filesystem web-asset upload.

[Certain] The method uses a fixed 600-second recording and concurrent observer tally, ten 60-second half-open windows, measured per-sensor DRDY rate, current-window mean removal, symmetric Hann, exact N-point FFT and largest positive in-band magnitude bin. Nine independent sensor-axis streams are preserved. A session median requires all ten valid estimates. Formal group/cell baselines use matching finalized accepted session medians. The descriptive +/-s interval and separate +/-2s review heuristic remain distinct.

[Certain] Traffic cutoffs are derived from actual equal-duration pilot counts; no field numeric cutoffs were invented. Pilot and formal controls, snapshot/hash, retained-count recovery, QC reasons, CRC32, export/replay and explicit backup/purge workflow are implemented.

## Reproduced Arduino build

[Certain] Final compile completed with exit code 0 after persistent AP credentials, calendar-null handling, precheck invalidation and source formatting changes. No hardware upload was performed.

- Arduino CLI 1.1.1, bundled with Arduino IDE.
- Espressif esp32:esp32 core 3.3.5.
- ArduinoJson 7.4.2; core libraries FS/Wire/LittleFS/Preferences/WebServer/Networking/WiFi/Hash 3.3.5.
- Final sketch usage: **1,115,179 bytes**; static internal dynamic-memory allocation reported: **55,704 bytes**, leaving 271,976 bytes in that compile report.
- Compiled application .bin is **1,115,328 bytes**.
- The CLI's custom-board metadata reports 16 MiB as maximum program size. This is not the app partition capacity. Independently decoded generated partition entries confirm the factory app is **3,145,728 bytes** at 0x10000, and the binary fits. LittleFS region is **13,565,952 bytes** at 0x310000, ending at 0x1000000.
- Static memory output does not include the runtime principal PSRAM allocations of **6,688,144 bytes** plus other runtime allocations.

Exact PowerShell command (compile only):

~~~powershell
& 'C:/Program Files/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe' compile --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,UploadMode=default,FlashMode=qio,FlashSize=16M,PSRAM=opi,PartitionScheme=custom,CPUFreq=240,LoopCore=1,EventsCore=1,EraseFlash=none' --libraries 'C:/Users/Jan Clyde Talosig/Documents/Arduino/libraries' --build-path 'C:/Users/Jan Clyde Talosig/AppData/Local/Temp/shm-firmware-build' 'D:/Antigravity/Projects/SHM-Capstone/Code Files/GPT Build/firmware/SHM_Capstone'
~~~

[Certain] arduino_compile_20261024.txt retains the actual compile output. firmware_manifest_20261024.json records source SHA256 and generated artifact hashes, partition decoding and toolchain parameters. The external library path is explicit because the IDE's configured sketchbook differs from the CLI's default.

## Executed numerical and record checks

[Certain] Native MSVC C++ linked the actual dsp.cpp and baseline.cpp; /std:c++17 /O2 /W4. Independent NumPy 2.3.5 full-complex FFT comparisons passed all **16 spectral/input cases** with seed 20261024. Worst normalized maximum complex error was approximately **1.10e-7**, below the chosen **2e-6 software tolerance**. Tested N includes 31,64,257,6000,6001,6200. Scalar/rate/median and baseline isolation/sample-statistics cases also passed. Exact cases/source hashes are in math_verification.json. This threshold is not an instrument accuracy claim.

[Certain] Final versions of the following independent workflow commands were rerun successfully using the bundled Python:

~~~powershell
python tools/verify_raw_pipeline.py
python tools/verify_traffic_workflow.py
~~~

[Certain] raw_pipeline_verification_20261024.txt records the generated 180,000-record/90-axis-window session, CRC corruption, injected jitter and sample-index-gap detection, all-ten median rule and unfrozen pilot handling. The script also checks metadata-driven near-tie tolerance. traffic_verification_20261024.txt records known tertiles, optional QC handling, rejection of twelve invalid pilot inputs and campaign context separation. Generated signals/counts are not observations from a bridge.

[Certain] Embedded browser JavaScript syntax and referenced DOM IDs were checked during UI implementation. Source/API integration was reviewed. No live-device browser/network operation or screenshot-based appearance validation is claimed.

## Verified design evidence

[Certain] Exact menu values were read from the installed 3.3.5 board metadata. N16R8 memory interfaces, USB and reserved pins were checked against the [Espressif module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf), [Tools menu guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/guides/tools_menu.html) and [partition guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/tutorials/partition_table.html).

[Certain] Hardware register values and nominal sensitivity/rate/filter/FIFO behavior were checked against manufacturer documents. VERIFIED_FIRMWARE_SOURCES.md records document IDs and verified current manufacturer-hosted links, including migration away from old TDK URLs. MATHEMATICAL_ALGORITHMS.md records the primary formula references and exact equation IDs.

## Corrections made during integration review

- Paired DRDY/FIFO only after stable equal counts; a permanent one-frame mismatch is an error.
- Avoided an acquisition pause deadlock when initial hardware initialization had not created the task.
- Guarded missing-worker live API and used atomic pause handshakes.
- Preserved gap checks across window boundaries and explicit QC reason/error metadata.
- Prevented pilot/invalid/context-mismatched records from receiving authoritative baseline comparisons.
- Compared against prior baseline before replaying the newly finalized session.
- Added pending count finalization using retained snapshots after reboot; finalized counts remain immutable.
- Kept absent calendar time as zero; MCU monotonic time remains the scientific timestamp.
- Invalidated precheck after storage maintenance/restarts.
- Persisted first-use random AP credential with NVS write/readback verification; normal external-power restarts keep it. Failed credential verification leaves AP stopped.
- Formatted root-owned C++ with bundled clang-format 14; pure numerical modules retained their audited hashes.
- Added supersession banners and current maps so historical Welch/old-pin/scaffold notes cannot be mistaken for the active contract.

## Limits and required prototype evidence

[Certain] No physical sensor, PCB, known-frequency reference, FIFO/DRDY trace, full device session, power-interruption recovery, Wi-Fi load endurance or field count has been measured in this work. Successful compilation establishes source/toolchain compatibility; numerical fixtures establish limited algorithm agreement.

[Likely] The proposed two-bus + three-DRDY map is workable on the named module, subject to carrier access, correct electrical design and measured timing. IRQ epochs include MCU latency and sensor delay. Independent clocks and sequential reads do not establish phase synchronization or spatial correlation.

[Certain] Whole-session RAM capture deliberately avoids flash writes during acquisition. Reset/power loss before successful post-capture persistence loses that session. Internal flash holds only a small number of complete raw recordings, so external backups and explicit purging are required.

[Certain] The band, timing tolerance, clock/count tolerance, clipping criterion, all-ten policy and baseline display count are prototype/protocol choices, not empirical validation. No calibrated frequency accuracy, verified natural mode, bridge safety finding, statistical power, 95% interval or structural diagnosis is claimed.

Next: follow PROTOTYPE_WORKFLOW.md and record real outcomes. GPT6 Astra independently audits via ASTRA_REVIEW_BRIEF.md; the user assigned later schematic/PCB work to Astra after prototype evidence and BOM work to GPT6.1 Sol after hardware definition.
