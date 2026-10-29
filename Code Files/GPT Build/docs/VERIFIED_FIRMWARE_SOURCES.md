# Firmware evidence and link ledger

Checked 2026-10-24. Distinguish manufacturer specifications, project choices, mathematical definitions, compilation and physical evidence. A working link or build is not a bench measurement. The algorithm audit map is maintained separately alongside the DSP implementation.

| ID | Primary source and link | What it supports / verification status |
| --- | --- | --- |
| HW-S01 | [Espressif ESP32-S3-WROOM-1 / 1U datasheet v1.8](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | PDF opened, 53 pages. Table 1-1 N16R8 memory types/capacities; Table 3-1 pin restrictions; USB, strapping and supply information. |
| HW-S02 | [Espressif hardware schematic checklist](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html) | Opened. Power, reset, USB, memory-pin restrictions and later hardware review inputs. |
| HW-S03 | [ESP32-S3 I2C reference](https://docs.espressif.com/projects/esp-idf/en/release-v4.4/esp32s3/api-reference/peripherals/i2c.html) | Opened. Two I2C controllers and bus pull-ups. This older reference establishes the SoC interface, not the active Arduino API version. |
| HW-S04 | [Arduino-ESP32 Wire API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/i2c.html) | Opened. Explicit pins, clock and master transaction API. Active implementation must use the installed version's signatures. |
| HW-S05 | InvenSense **RM-MPU-6000A-00 rev4.2**, 2013-08-19, [current PDF](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-04/rm-mpu-6000a-00-mpu-6000-register-map.pdf?VersionId=jEYAYvYOKeDIa.5IJgZPIlWgNTRCs.9m), [manufacturer entry](https://www.invensense.tdk.com/en-us/download-resource/rm-mpu-6000a-00-mpu-6000-and-mpu-6050-register-map-and-descriptions) | PDF opened, 46 pages. §§4.2–4.6, 4.14–4.17, 4.27–4.32 cover the driver. |
| HW-S06 | InvenSense **PS-MPU-6000A-00 rev3.4**, 2013-08-19, [current PDF](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-04/ps-mpu-6000a-00-mpu-6000-and-mpu-6050-datasheet.pdf?VersionId=eMVDQ08Qz7kahOvvE6xCs8WtRhxekFIH), [manufacturer entry](https://www.invensense.tdk.com/en-us/download-resource/ps-mpu-6000a-00-mpu-6000-and-mpu-6050-datasheet) | PDF opened, 52 pages. §§6.2–6.6 and 7.17 support scale, supply, addresses, timing and FIFO. |
| TOOL-S01 | [Arduino-ESP32 installing](https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html) | Opened. Stable package index and Boards Manager workflow. |
| TOOL-S02 | [Arduino-ESP32 Tools menu](https://docs.espressif.com/projects/arduino-esp32/en/latest/guides/tools_menu.html) | Opened. Generic S3 target, flash/PSRAM and USB menu concepts. Exact selected values additionally read from local 3.3.5 board metadata. |
| TOOL-S03 | [Espressif USB CDC upload guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/tutorials/cdc_dfu_flash.html) | Opened. Native USB connection, initial BOOT/RESET sequence and CDC settings; external UART bridges require their own transport configuration. |
| TOOL-S04 | [Arduino-ESP32 partition tables](https://docs.espressif.com/projects/arduino-esp32/en/latest/tutorials/partition_table.html) | Opened. CSV format, aligned offsets, factory app and sketch-local override. Partition sizes in this project are engineering choices. |
| TOOL-S05 | [Espressif release 3.3.12](https://github.com/espressif/arduino-esp32/releases/tag/3.3.12) | Official `/releases/latest` resolved here. Current stable at inspection; local core is 3.3.5. No claim of building against 3.3.12. |
| TOOL-S06 | [Earle Philhower LittleFS uploader](https://github.com/earlephilhower/arduino-littlefs-upload), [release 1.6.3](https://github.com/earlephilhower/arduino-littlefs-upload/releases/tag/1.6.3) | Author repository/release opened. External IDE extension supplies Ctrl+Shift+P upload command. Optional; not needed for embedded dashboard. |

## MPU-6050 legacy links and migration

The historical official [register-map URL](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf) and [product-specification URL](https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf) remain in search indexes with manufacturer document contents. Direct HTTP checks returned HTML redirects to the new manufacturer's search, rather than PDF files. The alternate `MPU-6000-Register-Map.pdf` returned 404. Do not label those old endpoints as live PDF downloads.

The new manufacturer [search for 6050](https://www.invensense.tdk.com/en-us/search-result?query=6050) lists the exact document IDs/version/date. Its public website search API returned the CloudFront download URLs above; both PDFs were opened and their identity/content verified. CloudFront is the manufacturer's current download host, not a substituted third-party datasheet. Confirm the returned content remains a PDF when retrieving it later. Device identity and actual register behavior still require the prototype.

## Local tool discovery (read-only)

- CLI: `C:/Program Files/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe`, version 1.1.1.
- Installed board core: `esp32:esp32` 3.3.5.
- Board: `esp32:esp32:esp32s3` / ESP32S3 Dev Module.
- Board/core files: `C:/Users/Jan Clyde Talosig/AppData/Local/Arduino15/packages/esp32/hardware/esp32/3.3.5`.
- ArduinoJson: 7.4.2 at `C:/Users/Jan Clyde Talosig/Documents/Arduino/libraries/ArduinoJson`.
- IDE settings file: `C:/Users/Jan Clyde Talosig/.arduinoIDE/arduino-cli.yaml`; sketchbook `d:/newbackup/documents/Arduino` differs from CLI default library location. No settings changed.
- Initial PATH/LLVM/MSYS checks found no host compiler. The later numerical verification located and used MSVC through its developer environment; see `tools/README.md` and the numerical verification report. PATH discovery alone did not establish compiler availability.

For mathematical references, use the equation IDs and source map supplied with `dsp.cpp`, `baseline.cpp`, the offline replay tool and their review documentation. FFT peak selection, descriptive sample SD, and a separate heuristic review band follow the approved paper. Hardware nominal settings, timing tolerances, pilot decisions and synthetic verification must be labeled separately from measured field findings.
