# Arduino IDE setup — ESP32-S3-WROOM-1-N16R8

Updated 2026-10-24. The user approved the paper and authorized firmware development. The active sketch is `firmware/SHM_Capstone/SHM_Capstone.ino`. Use Arduino IDE 2.x and the Espressif `esp32` package; this is an Arduino sketch with peer `.cpp` and `.h` modules.

## Version and installation

The integrated sketch compiled with Espressif `esp32:esp32` **3.3.5**, Arduino CLI **1.1.1** bundled in Arduino IDE, and ArduinoJson **7.4.2**. The final integration build reported **1,115,179 application bytes** and **55,704 bytes of static RAM**; runtime PSRAM allocations are additional. See the implementation report for the actual command and build evidence. The official release page returned **3.3.12** as the latest stable release on 2026-10-24; it has not been installed or validated for this revision. Preserve a recorded, working version during the pilot.

1. Install Arduino IDE 2.x from Arduino.
2. In **File → Preferences → Additional boards manager URLs**, add the [Espressif stable index](https://espressif.github.io/arduino-esp32/package_esp32_index.json).
3. In Boards Manager, install **esp32 by Espressif Systems**, version **3.3.5** to reproduce this environment. The distinct package named Arduino ESP32 Boards is not the generic board package used here.
4. Install **ArduinoJson by Benoit Blanchon**, version **7.4.2**, through Library Manager if the sketch uses it. WiFi, Wire, WebServer, Preferences, and LittleFS are supplied by the Espressif core.
5. Open the matching `.ino` in the sketch folder. Keep `partitions.csv` beside it.

## Tools menu

These menu names and values were read from installed Espressif core 3.3.5 `boards.txt` through `arduino-cli board details`. The N16R8 module has 16 MB **Quad SPI flash** and 8 MB **Octal SPI PSRAM**; its flash and PSRAM use different interface modes. [Module datasheet, Table 1-1](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)

| Tools setting | Value for the proposed native USB prototype | Reason |
| --- | --- | --- |
| Board | **ESP32S3 Dev Module** | Generic ESP32-S3 target, FQBN `esp32:esp32:esp32s3` |
| USB Mode | **Hardware CDC and JTAG** | Native USB serial/JTAG controller |
| USB CDC On Boot | **Enabled** | Makes `Serial` use native USB CDC |
| Upload Mode | **UART0 / Hardware CDC** | Core's upload choice for this USB mode |
| USB Firmware MSC On Boot | **Disabled** | No USB disk service required |
| USB DFU On Boot | **Disabled** | CDC upload and monitoring used |
| CPU Frequency | **240MHz (WiFi)** | Reproducible prototype setting |
| Flash Mode | **QIO 80MHz** | N16R8 flash is quad; do not select OPI flash |
| Flash Size | **16MB (128Mb)** | Physical module capacity |
| PSRAM | **OPI PSRAM** | R8 is 8 MB octal PSRAM |
| Partition Scheme | **Custom** | Uses sketch-local `partitions.csv` |
| Arduino Runs On | **Core 1** | Composition loop; acquisition task placement is set in code |
| Events Run On | **Core 1** | Recorded baseline menu setting |
| Core Debug Level | **None** | Avoid verbose serial output during acquisition |
| Erase All Flash Before Sketch Upload | **Disabled** | Preserve existing session files and NVS |
| Upload Speed | **115200** initially | Conservative UART fallback; native USB speed is transport controlled |
| Port | Port belonging to the board's programming connector | Re-select after first native USB reset if it changes |

The official [Tools menu guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/guides/tools_menu.html) describes these controls. A development carrier may have two USB connectors; inspect its wiring/labels before choosing the port.

## Native USB versus USB-to-UART carrier

The one USB-C connector in the intended custom board supplies external power and carries USB data. Native USB uses **GPIO19 D−** and **GPIO20 D+**. USB VBUS must feed the approved power circuit, not the module's 3.3 V pin directly. The firmware pin map reserves both data pins.

For the first native USB upload, hold **BOOT**, press and release **RESET**, then release BOOT and select the newly enumerated port. Upload; reset once if needed. Later CDC uploads can normally reset automatically. Open Serial Monitor at **115200**. Do not leave acquisition waiting for `Serial` to connect. [Espressif CDC upload procedure](https://docs.espressif.com/projects/arduino-esp32/en/latest/tutorials/cdc_dfu_flash.html)

At the first bench boot, privately record the generated access-point password printed to Serial. It is retained in NVS, so normal external USB power boots reuse it without a serial host. A whole-flash erase changes that password and removes campaign settings/logs; LittleFS-only formatting preserves the password. See `PROTOTYPE_WORKFLOW.md` for operation.

If the prototype carrier instead connects USB-C to a CH340/CP210x/other UART bridge, use that bridge's COM port. Set **USB CDC On Boot → Disabled** when `Serial` diagnostics should use UART0. UART0 is GPIO43 TX / GPIO44 RX; the upload mode remains UART0 / Hardware CDC. Keep this variation in the session/build notes because its serial transport differs. Do not infer the connector wiring from the module marking alone.

## Flash partition and session capacity

The revision uses one 3 MiB factory application and the remaining large filesystem region for measurements. Confirm the actual checked-in CSV before flashing. The intended map is:

| Region | Offset | Size |
| --- | --- | --- |
| NVS | `0x9000` | `0x5000` (20 KiB) |
| Reserved OTA selection metadata | `0xE000` | `0x2000` (8 KiB) |
| Factory application | `0x10000` | `0x300000` (3 MiB) |
| LittleFS partition, label `spiffs` | `0x310000` | `0xCF0000` (13,565,952 bytes) |

The last region ends at `0x1000000`, exactly 16 MiB. The reserved OTA metadata does not provide an OTA update slot; this map has one application. LittleFS in this core uses a data partition with SPIFFS subtype/label; the subtype name does not mean the firmware is mounting the SPIFFS filesystem. Arduino's build system automatically takes a sketch-local `partitions.csv`. [Espressif partition guide](https://docs.espressif.com/projects/arduino-esp32/en/latest/tutorials/partition_table.html)

Capacity is computed from the actual serialized record size, `3 × fs × 600 × record_bytes`, plus headers, summaries, filesystem metadata, and reserve. `RawRecord` is **32 bytes**. At nominal 100 Hz per sensor the payload is **5,760,000 bytes per ten-minute session**, plus the 32-byte raw header and other files. The start check reserves the maximum 200,000-record buffer size plus 262,144 bytes: **6,662,144 free bytes**. Do not assume 15 sessions fit internally. Export recordings to the host and explicitly purge only selected exported raw files between runs as needed. Purging raw retains summaries used for baselines; keep the downloaded raw files as research evidence.

The firmware allocates **6,400,000 bytes of PSRAM** for the 200,000 raw records. The 6,500-sample axis scratch array adds 26,000 bytes; the two 16,384-element complex FFT work arrays add 262,144 bytes. These explicit allocations total **6,688,144 bytes**, before other buffers and allocator overhead. OPI PSRAM must initialize successfully; the dashboard reports whether allocation succeeded.

Acquisition writes records to PSRAM for the whole 600-second interval. DSP processes completed windows concurrently. After capture ends and queued window jobs complete, firmware suspends acquisition and writes the raw file, window table and summary to LittleFS. It then resumes acquisition. Network maintenance and flash mutations are blocked during an active recording/processing phase. This design avoids filesystem writes inside the acquisition interval but means a reset/power loss before persistence can lose that interval; retain power through processing and confirm the stored-session state before disconnecting. PSRAM is working memory and is not archival storage.

## Web server, WebSocket, and the data folder

The prototype serves the dashboard's embedded HTML/CSS/JavaScript from the firmware through HTTP. Compile and upload the sketch normally; **no filesystem upload is required to install the dashboard**. LittleFS is used for session data.

HTTP/WebSocket describe network protocols. Embedded strings versus a `data/` filesystem image describe where assets are stored. Either protocol can be used with either storage method; a WebSocket does not require LittleFS or a `data/` folder. This revision uses HTTP endpoints and browser polling; inspect `web_server.cpp` and the API contract for implemented routes.

The prior `data/` dashboard scaffold is historical/reference material if retained. Editing it does not alter a dashboard compiled from an embedded header. Follow the current UI source indicated by the project map.

### Optional future filesystem asset upload

The **Ctrl+Shift+P → Upload LittleFS to Pico/ESP8266/ESP32** command belongs to the external [Earle Philhower uploader extension](https://github.com/earlephilhower/arduino-littlefs-upload), not a default Arduino IDE command. Its [1.6.3 release](https://github.com/earlephilhower/arduino-littlefs-upload/releases/tag/1.6.3) was current when checked; the author's README requires IDE 2.2.1 or later. If a future revision moves web assets to LittleFS, follow that extension's installation instructions and record its version. Close Serial Monitor before uploading and use the matching board/partition settings.

**A filesystem-image upload can replace the measurement partition and its existing logs.** Export files first and perform it only as an explicit maintenance step. This prototype requires no such upload. First-use filesystem initialization must also be explicit; a mount error must never silently format recorded data.

## Reproducible local CLI compile

The CLI invokes the same Arduino core as the IDE; it is useful for repeatable build records. This example compiles without uploading:

```powershell
$taskCli = 'C:/Program Files/Arduino IDE/resources/app/lib/backend/resources/arduino-cli.exe'
$taskSketch = 'D:/Antigravity/Projects/SHM-Capstone/Code Files/GPT Build/firmware/SHM_Capstone'
$taskFqbn = 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,UploadMode=default,CPUFreq=240,FlashMode=qio,FlashSize=16M,PSRAM=opi,PartitionScheme=custom,LoopCore=1,EventsCore=1,EraseFlash=none'
& $taskCli compile --fqbn $taskFqbn --libraries 'C:/Users/Jan Clyde Talosig/Documents/Arduino/libraries' $taskSketch
```

On this machine, CLI default data is `C:/Users/Jan Clyde Talosig/AppData/Local/Arduino15`, core is `packages/esp32/hardware/esp32/3.3.5`, and ArduinoJson 7.4.2 is at `C:/Users/Jan Clyde Talosig/Documents/Arduino/libraries/ArduinoJson`. The IDE's existing `C:/Users/Jan Clyde Talosig/.arduinoIDE/arduino-cli.yaml` points its sketchbook to `d:/newbackup/documents/Arduino`; ensure Library Manager installs dependencies in the selected IDE sketchbook or supply the library path in CLI. No global IDE settings were changed by this revision.

Record the full FQBN, Arduino core version, library versions, firmware/configuration ID, build output, and hardware carrier for each frozen field release. Compilation establishes source/toolchain compatibility; the bench checks in `HARDWARE_INTERFACE.md` establish the electrical and timing behavior.

Follow `PROTOTYPE_WORKFLOW.md` for the first boot, explicit blank-filesystem initialization, pilot recording, offline replay, threshold derivation, formal recording and backup sequence.
