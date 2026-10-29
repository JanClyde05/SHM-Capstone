# Web interface and offline assets

## Active implementation and decision

[Certain] `firmware/SHM_Capstone/web_server.cpp` uses the `WebServer` supplied by the Arduino-ESP32 core. `ui_assets.h` contains three flash-resident literals: `SHM_INDEX_HTML`, `SHM_STYLE_CSS`, and `SHM_APP_JS`. The dashboard requires no external libraries, CDN, internet connection, or filesystem asset upload. Edit these literals when changing the active UI.

[Certain] The previous `data/index.html`, `data/style.css`, and `data/app.js` are an inactive scaffold snapshot. They are not loaded or served by this firmware. The latest user allowed choosing embedded assets; this decision supersedes the older LittleFS hosting instruction in `ARDUINO_IDE_AND_UI_STANDARD.md`. LittleFS scientific storage is independent of web hosting. Never upload the old `data/` image over a filesystem containing measurement records.

HTTP and WebSocket describe transport. Embedded flash and LittleFS describe where assets are stored. Either transport can be used with either storage option; a WebSocket does not require a `data/` directory. This build chooses HTTP REST and completion-driven polling, approximately once per second, to keep the prototype dependency set small. There is no WebSocket server or uploader extension requirement.

## Access point and connection

[Certain] `wifi_manager.cpp` starts an AP with a device-specific `SHM-xxxxxx` SSID and a generated 16-character password. On first use, the password is persisted to NVS namespace `shm-network`, key `ap-pass`; subsequent boots reuse it, allowing operation from external power. The password and address are printed on USB Serial. Open the printed `http://.../` URL after connecting a phone/computer to that AP. Disable automatic switching away from a network without internet if the client does that. A maximum of two clients is configured. No human-selected default secret is committed. Network joining and credential entry are not implemented in this prototype.

[Certain] First-use password bytes are obtained after enabling Wi-Fi in unconnected STA mode and use rejection sampling over the configured alphabet; field operation then switches to AP mode. The code verifies the NVS write length and exact readback before starting the AP. An unavailable NVS namespace, invalid stored credential, write/readback mismatch or radio error stops the AP and prints a Serial diagnostic; there is no open-network fallback. Credentials are never returned by an API or written into scientific records. See Espressif's [Wi-Fi API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/wifi.html), [Preferences API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/preferences.html) and [random-number generation notes](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/random.html).

Normal reset, power cycling and a firmware upload preserving NVS retain this password. Read it again using USB Serial if needed and record it before an externally powered field run. Whole-flash erase clears NVS and causes a new password on the next boot; it also removes stored measurements and campaign settings, so back them up before choosing that operation. Formatting only the measurement filesystem does not clear this NVS key. There is no dashboard credential-reset route. If NVS is unreadable, use USB Serial for its diagnostic and back up recoverable records before any deliberate flash reset.

## Module boundary

`app.cpp` supplies `WebApiCallbacks` through `webServerConfigure` before `webServerBegin`. The web layer parses transport fields; the app/session owner performs numerical validation, state gating, configuration hashing, and all scientific operations.

| Callback | Responsibility |
|---|---|
| `getJson(route)` | Return a small JSON snapshot or an empty string for unavailable resources. |
| `postForm(route, fields, responseJson, responseStatus)` | Validate the command and return true when the route is handled. |
| `openDownload(sessionId, kind, file, mime, filename)` | Open an approved retained file for download. |
| `isCapturing()` | True during PRECHECK, ARMED, RECORDING or PROCESSING; suppress bulk transfers. |

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/`, `/index.html`, `/style.css`, `/app.js` | Embedded dashboard assets; refused during acquisition/processing. Open dashboard before capture. |
| GET | `/api/status` | State and readiness snapshot. |
| GET | `/api/live` | Latest raw XYZ, measured rates, and nine channel peak results. |
| GET | `/api/config` | Frozen state, hash, analysis band, timing tolerance, traffic cutoffs. |
| GET | `/api/baseline` | Statistics per sensor, axis, and traffic class. |
| GET | `/api/sessions` | Retained session index. |
| POST | `/api/session/precheck` | Request/check hardware readiness through the app owner. |
| POST | `/api/session/start` | Begin a pilot/formal 600-second session. |
| POST | `/api/session/stop` | Abort capture; dashboard asks for confirmation. |
| POST | `/api/session/finalize` | Attach the observed vehicle total to the session awaiting count. |
| POST | `/api/config/freeze` | Freeze pilot-selected settings after explicit `FREEZE` entry. |
| GET | `/api/sessions/{id}/raw` | Download raw binary record. |
| GET | `/api/sessions/{id}/windows` | Download per-window CSV results. |
| GET | `/api/sessions/{id}/summary` | Download session JSON summary. |

Mutations require `application/x-www-form-urlencoded` and `X-SHM-Request: local`. No cross-origin access is enabled. The transport rejects more than 16 fields and fields longer than 256 characters; the owner applies tighter per-field limits as needed. There is no deletion, formatting, file upload, Wi-Fi credential, or arbitrary filesystem endpoint. Download IDs accept letters, digits, underscore and hyphen only (at most 64 characters). Only the three named record kinds are allowed.

`WebForm` maps fields to C++ members as follows:

| HTTP field | C++ member |
|---|---|
| `mode` | `mode` |
| `operator` | `operatorName` |
| `weather_note` | `weatherNote` |
| `station_id` | `stationId` |
| `orientation` | `orientation` |
| `epoch` | `epoch` (Unix seconds, browser clock) |
| `vehicle_count` | `vehicleCount` |
| `session_id` | `sessionId` |
| `cutoff1`, `cutoff2` | `cutoff1`, `cutoff2` |
| `band_lo`, `band_hi` | `bandLo`, `bandHi` |
| `timing_tolerance_us` | `timingToleranceUs` |
| `confirm` | `confirm` |

The start request uses mode/operator/station/orientation/weather/epoch. Mode values are lowercase `pilot` and `formal`. Count finalization uses session ID and integer vehicle count. The freeze request uses the two count cutoffs, frequency band, timing tolerance and confirmation, plus the station ID and orientation copied from the Session details fields above it. Both are trimmed consistently before start and freeze requests. Frozen configuration binds formal sessions to the same exact station/orientation strings. Actual frozen station/orientation are restored into empty form fields on reconnection. Traffic class follows counts, rather than the operator selecting a desired class.

After start, ARMED is a five-second preparation interval. `/api/status.starts_in_s` supplies the countdown; `/api/status.elapsed_s` supplies recording progress. The dashboard shows when to begin the concurrent vehicle tally. Stop is available during ARMED and RECORDING and produces an incomplete record. PRECHECK is a ten-second readiness interval. Its success is required before the start button becomes available. A UI countdown is an operator aid; physical acquisition timing is determined and recorded by the firmware.

## Dashboard data shape

`/api/status` supplies `state`, `fw_version`, `hw_rev`, `session_id`, `elapsed_s`, `starts_in_s`, `hardware_ready`, `psram_ready`, `storage_ready`, `free_bytes`, `precheck_ready`, and `message`. Readiness means the firmware's current checks; it is not a field-validation result. Start requires the three readiness flags plus a completed precheck. The lifecycle values are `IDLE`, `PRECHECK`, `ARMED`, `RECORDING`, `PROCESSING`, `AWAITING_COUNT`, `COMPLETE`, and `ERROR`. `/api/live` repeats the current state. The UI checks these lifecycle values independently of baseline labels.

The active dashboard uses `/api/live.sensors[0..2]` with `id`, `xyz_g: [x,y,z]`, `fs_est_hz` and `axes.{x,y,z}`. Each axis has `valid_peak`, `f_d_hz`, and `baseline_state`; `snr_db` is optional and displayed as unavailable when absent. Top-level live fields include `state`, `session_id`, `traffic_level`, `windows_complete`, and `total_windows`; elapsed time is read from status. The sensor selector changes the frequency and baseline displays without mixing sensor streams. A second synchronized selector is present on the baseline page. The nine-row results table preserves channel identity. When overall sensor readiness is false the raw XYZ display remains unavailable.

The current API does not compute or return SNR, and the dashboard displays `SNR — dB` accordingly. It shows actual largest-bin peak results supplied by the numerical module. Raw XYZ comes from the latest actual acquisition frame; live frequency values come from the latest completed window, rather than a synthesized signal or a continuously refitted curve.

`/api/baseline.sensors[0..2].axes.{axis}.levels.{NEAR_ZERO,MEDIUM,HEAVY}` contains `n`, `mean_hz`, `sd_hz`, `cv_pct`, and `state`. `/api/config` uses `frozen`, `hash`, `band_lo`, `band_hi`, `timing_tolerance_us`, `cutoff1`, `cutoff2`, `station_id`, and `orientation`. `/api/sessions.sessions[]` uses `session_id`, `mode`, `traffic_level`, `valid`, `finalized`, `duration_s`, and `vehicle_count`. The UI labels unfinalized records COUNT PENDING and finalized records QC COMPLETE or REVIEW QC. This session display does not assert that all nine stream medians meet the per-stream acceptance conditions.

The exact assessment display labels remain `NO BASELINE YET`, `PROVISIONAL (n<5)`, `WITHIN BASELINE`, and `OUTSIDE BASELINE – REVIEW`. Transport enums `NOT_READY`, `PROVISIONAL_BASELINE`, `WITHIN_BASELINE`, and `OUTSIDE_BASELINE_REVIEW` map to those labels. These labels describe the internal frequency comparison only. Session lifecycle states are separate.

Static baseline tables additionally render the API availability state `BASELINE_READY` as `BASELINE READY`. This states that reference statistics are available; it does not compare a current frequency. The live sensor-axis `baseline_state` remains authoritative for the four measurement-review labels. Refreshing a statistics table cannot replace a current live comparison with a static availability label.

If a reboot occurs after raw data, window results and a pending summary were persisted, the record remains visible as COUNT PENDING. The count form keeps its session-ID field editable: enter that retained record's ID and the concurrent count from the field sheet, then submit while the device is idle. Session finalization owns recovery and validation of the stored summary. The browser does not invent or infer a missing tally, restart acquisition, or convert an incomplete capture into a full session. During a normal AWAITING_COUNT session, the current ID is filled automatically.

Stored-count recovery updates that retained summary and refreshes the static baseline table. It does not load the old session into the current live acquisition buffers. Download its summary/windows/raw record to inspect that recovered session's results. The session list returns up to 64 retained summaries in filesystem iteration order; its displayed record count is the returned list length, not a campaign-wide total. Browser views of records and static statistics can remain visible after a disconnect; the node connection pill and blank live readings identify the disconnected state.

## Timing and scientific limits

[Certain] The browser makes status and live requests sequentially, then schedules the next cycle one second after completion; it never starts another polling cycle while one is pending. Its request timeout is 4.5 seconds. Session/baseline/config lists are refreshed while idle and on state transitions. File streaming and bulk asset transfer are rejected during PRECHECK/ARMED/RECORDING/PROCESSING. This is a synchronous web server, so it does not promise hard realtime response or acquisition timing. Acquisition must record actual timing and enforce its own QC.

The dashboard never synthesizes readings or curves. Missing numbers display em dashes. It reports each sensor's independent XYZ readings, does not label a sensor as one axis, and leaves vertical direction to recorded orientation. Readiness and errors remain the application owner's responsibility. A field run must not be described as verified solely because its dashboard connects.

## Sources and actual checks

[Certain] Official API declarations checked for `on`, `collectHeaders`, `arg`, `send_P`, `streamFile`, and `handleClient`: [Arduino-ESP32 WebServer source](https://github.com/espressif/arduino-esp32/blob/master/libraries/WebServer/src/WebServer.h). Access-point configuration checked against the Espressif Wi-Fi API linked above. Links checked 2026-10-24.

[Certain] Embedded JavaScript passed `node --check` after generation. [Not verified] Browser/device rendering, AP connection, route responses, download completeness, client disconnections, and concurrent acquisition timing require the integrated build and physical prototype. Compilation status belongs in the main implementation report after the full sketch has been built.
