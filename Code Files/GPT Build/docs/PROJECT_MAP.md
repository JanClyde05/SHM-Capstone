# Project navigation map

| Path | Responsibility / next reader |
|---|---|
| firmware/SHM_Capstone/SHM_Capstone.ino | setup/loop entry only |
| app.cpp | composition, API registration and explicit Serial storage commands |
| config.h | fixed session/window/nominal settings and pilot analysis config |
| hardware_profile.h | proposed N16R8 two-bus/DRDY GPIO map |
| imu_mpu6050.cpp | verified register writes/readback, accel FIFO, DRDY pairing |
| acquisition.cpp | dedicated core1 task, sequential complete XYZ frames, independent indices and rate preview |
| measurement_types.h | exact32-byte binary header/record layout |
| session.cpp | lifecycle, immutable600s raw buffer,60s window jobs, QC, traffic finalization, config hash, baseline replay |
| dsp.cpp / dsp.h | pure C++ exact N-point transform, Hann, maximum-bin frequency; EQ-* labels |
| baseline.cpp / baseline.h | pure C++ Welford/sample SD/CV/review statistics; EQ-* labels |
| storage.cpp | LittleFS retention, CRC32, explicit format/raw purge helpers |
| timebase.cpp | monotonic epoch and optional browser calendar mapping |
| web_server.cpp / wifi_manager.cpp | HTTP REST and device AP |
| ui_assets.h | active embedded global-style UI; previous data/ files inactive |
| partitions.csv | factory3MB app and remaining LittleFS in16MB flash |
| tools/reference_math.py | independent NumPy formulas |
| tools/analyze_session.py | exact binary/CRC/timing/window/median reconstruction |
| tools/analyze_campaign.py | descriptive formal-session baseline cells |
| tools/verify_math.py / native_math_check.cpp | executable C++/NumPy audit |
| tools/verify_raw_pipeline.py | synthetic full-session decoder/QC audit |
| tools/derive_traffic_cutoffs.py / verify_traffic_workflow.py | real pilot cutoff derivation and independent input/context checks |
| docs/MATHEMATICAL_ALGORITHMS.md | Astra's equation/code/source registry |
| docs/DATA_FORMAT.md | binary, JSON and CSV schema; recovery semantics |
| docs/ARDUINO_IDE_SETUP.md | board menus, libraries, partitions and upload |
| docs/HARDWARE_INTERFACE.md | wiring, registers, DRDY assumptions and bench checks |
| docs/PROTOTYPE_WORKFLOW.md | operator sequence from first flash to pilot, freeze, formal sessions and backup |
| docs/ASTRA_REVIEW_BRIEF.md | independent mathematics audit scope, equation/function map and repeatable commands |
| field/log_sheet_template.csv | accompanying actual field notes and file/backup tracking |
| docs/VERIFIED_FIRMWARE_SOURCES.md | primary sources and local toolchain inventory |
| docs/WEB_INTERFACE.md | APIs and HTTP/WebSocket/LittleFS distinction |
| docs/IMPLEMENTATION_STATUS.md / reports/ | actual verification and outstanding physical work |
| hardware/rev2 / hardware/bom | future Astra hardware and Sol BOM stage |
| docs/01..07, firmware_legacy | historical source material; see current-method supersession banner |

Read AGENTS.md and HANDOFF.md before modifying this build. Original source program, manuscript, source MD Files and old hardware are reference-only inputs. Update this map and handoff whenever modules, protocols, equations or dependencies change.
