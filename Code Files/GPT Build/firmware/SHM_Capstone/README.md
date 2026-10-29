# SHM_Capstone

Arduino IDE entry SHM_Capstone.ino; target ESP32-S3-WROOM-1-N16R8 plus three MPU6050 ICs. Core math is portable C++; hardware/network/session code uses Arduino-ESP32.

Read ../../docs/ARDUINO_IDE_SETUP.md before Verify/Upload. Use the peer partitions.csv,16MB QIO flash,8MB OPI PSRAM, native USB menu choice matching your connector, and ArduinoJson7.4.2. Do not upload the inactive data/ folder.

At boot Serial prints the AP name and random password. Connect, open192.168.4.1 and run precheck. On a new blank filesystem, explicitly send FORMAT_ERASE_ALL via Serial first. Start pilot mode, observe5s countdown, tally concurrently for600s, wait for persistence, finalize count and export all3 files. Freeze pilot-derived settings/cutoffs/station/orientation before formal mode.

A raw file occupies about5.76MB; raw capture buffer reserves6.4MB PSRAM. Power interruption before persistence loses the RAM recording. Never claim a physical test was passed from the numerical verification report.
