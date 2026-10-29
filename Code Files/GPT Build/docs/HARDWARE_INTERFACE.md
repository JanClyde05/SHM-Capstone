# Hardware interface and acquisition contract

Updated 2026-10-24. User-confirmed target: **ESP32-S3-WROOM-1-N16R8** and **three bare MPU-6050 ICs**, co-located on one planned PCB. External supply connects through the programming USB-C connector. This document defines a prototype firmware interface for bench work; it is not a released schematic, PCB, or BOM.

## Prototype net assignment

GPIO numbers below are ESP32 signal numbers, not module pad numbers. `hardware_profile.h` is the firmware source of truth. Check the exact development carrier and the future schematic against this table before applying power.

| Device/net | ESP32 GPIO/controller | Device address / connection |
| --- | --- | --- |
| I2C bus 0 SDA | GPIO8 / controller 0 | IMU1 + IMU2 SDA |
| I2C bus 0 SCL | GPIO9 / controller 0 | IMU1 + IMU2 SCL |
| IMU1 AD0 | — | Fixed low, seven-bit address `0x68` |
| IMU2 AD0 | — | Fixed high to VLOGIC, seven-bit address `0x69` |
| I2C bus 1 SDA | GPIO10 / controller 1 | IMU3 SDA |
| I2C bus 1 SCL | GPIO11 / controller 1 | IMU3 SCL |
| IMU3 AD0 | — | Fixed low, seven-bit address `0x68` |
| IMU1 INT | GPIO4 | Separate data-ready timing input |
| IMU2 INT | GPIO5 | Separate data-ready timing input |
| IMU3 INT | GPIO6 | Separate data-ready timing input |
| USB D− / D+ | GPIO19 / GPIO20 | Reserved for native USB |
| UART0 TX / RX | GPIO43 / GPIO44 | Optional programming/diagnostic fallback |

The ESP32-S3 has two I2C controllers. Each MPU-6050 has only two address choices, selected by AD0, so three ICs cannot share one unsegmented bus with fixed unique addresses. Two controllers allow the above arrangement without an I2C multiplexer. Use 400 kHz only after signal integrity and pull-ups are checked. [Espressif I2C guide](https://docs.espressif.com/projects/esp-idf/en/release-v4.4/esp32s3/api-reference/peripherals/i2c.html), [Arduino Wire API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/i2c.html)

On the R8 module, **GPIO35/36/37 are reserved by the internal octal PSRAM**. Avoid boot strapping GPIO0/3/45/46 for sensor signals. The module has 16 MB quad flash and 8 MB octal PSRAM. [Espressif module datasheet, Tables 1-1 and 3-1](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)

## Bare IC requirements for the later hardware review

Bare MPU-6050 ICs require their own supply/logic connections, local decoupling and charge-pump components, pull-ups, defined AD0/FSYNC levels, and correct package orientation. A breakout board's regulator or pull-ups are not present in a bare IC. Confirm all details from the manufacturer's product specification and its typical operating circuit before the KiCad phase. Use a regulated 3.3 V design for this interface; never connect USB's 5 V directly to either ESP32 or MPU-6050 supply/logic pins. Keep all three accelerometer orientations declared and mechanically rigid at the roadway-deck station. Three co-located sensors provide three measurement channels; they do not establish a spatial mode shape.

The MPU-6050 product specification lists VDD **2.375–3.46 V**, VLOGIC **1.71 V to VDD**, I2C up to **400 kHz**, AD0 addresses `1101000`/`1101001`, and a **1024-byte FIFO**. [Verified manufacturer PDF, rev3.4, §§6.3–6.4 and 7.17](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-04/ps-mpu-6000a-00-mpu-6000-and-mpu-6050-datasheet.pdf?VersionId=eMVDQ08Qz7kahOvvE6xCs8WtRhxekFIH)

## Register audit map

Primary document: InvenSense **RM-MPU-6000A-00 revision 4.2, 2013-08-19**, [verified manufacturer PDF](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-04/rm-mpu-6000a-00-mpu-6000-register-map.pdf?VersionId=jEYAYvYOKeDIa.5IJgZPIlWgNTRCs.9m). Register numbers remain useful navigation anchors even if hosting changes. Values below are the selected configuration, not measurements. Code anchors `REG-POWER-01`, `REG-CLOCK-01`, and `REG-FIFO-01` identify reset, clock and FIFO setup respectively.

| Register | Address | Selected value or interpretation |
| --- | --- | --- |
| SMPLRT_DIV | `0x19` | `9`, divider for nominal 100 Hz |
| CONFIG | `0x1A` | `0x04`, DLPF_CFG=4, EXT_SYNC_SET=0 |
| ACCEL_CONFIG | `0x1C` | `0x00`, ±2 g / 16384 counts per g |
| FIFO_EN | `0x23` | `0x08`, accelerometer XYZ only |
| INT_PIN_CFG | `0x37` | `0x00`, active high push-pull, 50 µs pulse |
| INT_ENABLE | `0x38` | DATA_RDY bit0; overflow enable bit4 optional |
| INT_STATUS | `0x3A` | DATA_RDY bit0 / overflow bit4; reading clears status |
| ACCEL_XOUT_H…ZOUT_L | `0x3B`…`0x40` | Signed XYZ, high byte first |
| USER_CTRL | `0x6A` | FIFO enable bit6; reset bit2 while enable=0 |
| PWR_MGMT_1 | `0x6B` | DEVICE_RESET bit7; awake PLL-X clock selection `0x01` |
| PWR_MGMT_2 | `0x6C` | Leave gyro clock source operating; no axis standby |
| FIFO_COUNTH / COUNTL | `0x72` / `0x73` | Read high then low together |
| FIFO_R_W | `0x74` | Repeated FIFO byte reads |
| WHO_AM_I | `0x75` | Expect `0x68` at either AD0 address |

The gyro need not be written to the FIFO even while its clock remains active. On MPU-6050, USER_CTRL's I2C_IF_DIS must always remain zero. Reset FIFO with writes `USER_CTRL=0`, then `0x04`, then enable `0x40`, following sensor configuration and settling. Read back configuration registers before starting a session. Never read an empty FIFO as if it held new measurements.

## Timing equations and limits

**HW-EQ-01 — device sample-rate divider:**

`fs_nominal = 1000 / (1 + SMPLRT_DIV) = 100 Hz` for DLPF_CFG=4.

This is the device's nominal clock-derived rate. Each IC owns an independent oscillator. Measure its rate from its own data-ready sequence; do not assume all three run at exactly 100.000 Hz.

**HW-EQ-02 — FIFO capacity:**

`floor(1024 / 6) = 170` complete acceleration XYZ frames, approximately `170/100 = 1.70 s` at nominal rate.

This is a capacity estimate, not an allowed service delay. Drain frequently, retain reserve, detect overflow and mismatches, and reject affected windows. Host stalls during flash writes or downloads can exhaust it.

The current driver rejects an asserted overflow flag or FIFO occupancy of at least 1024 bytes. The DRDY queue holds 128 timestamps, so actual permitted host latency is shorter than the theoretical FIFO capacity. Recording uses a PSRAM buffer; flash persistence takes place after capture while acquisition is suspended. A five-second countdown following the start-time sensor reset/wake precedes the recorded interval.

The acquisition service drains one complete oldest XYZ frame from sensor 1, then sensor 2, then sensor 3, and repeats. Each record carries sensor ID, sensor sample index, polling-cycle ID and timing metadata. The polling-cycle ID denotes host service order, not simultaneous physical conversion. FIFO and data-ready timestamp queues must be paired in the same per-sensor order. Do not create artificial samples when an interrupt or FIFO frame is lost.

Before pairing, the driver snapshots the DRDY queue count before/after reading FIFO occupancy. It retries when those snapshots differ, when complete-frame count differs from timestamp count, or when FIFO bytes are not a multiple of six. A mismatch lasting more than 100 ms stops acquisition. This guards against silently accepting a permanent one-frame offset while allowing a transient conversion during the snapshot. The sensor sample index counts retrieved frames and persists across sensor restarts within the same MCU boot; window checks require consecutive values, not a zero first index.

An interrupt timestamp is the ESP32's observation of a digital data-ready edge. It includes interrupt latency and does not equal an independently calibrated ADC conversion instant. With DLPF_CFG=4 the manufacturer's accelerometer table specifies **21 Hz bandwidth and 8.5 ms delay**. The gyro column's 20 Hz / 8.3 ms values must not be used to describe acceleration. This filter is an acquisition setting, not proof that all out-of-band energy is removed. Account for its attenuation and remaining aliasing during the pilot.

Each sensor's host edge timing can establish average rate and gaps, but sequential polling plus independent IC clocks does not establish phase synchronization, cross-sensor coherence, or mode shapes. Independent per-axis dominant-frequency estimation remains the research task. Do not present agreement across three ICs as an externally traceable reference validation.

## Required prototype evidence

1. Confirm the carrier exposes the proposed GPIOs and that IMU supplies, VLOGIC, AD0, pull-ups, FSYNC and INT are correctly wired.
2. Inspect I2C rise times/transactions, scan each bus separately, and read `WHO_AM_I` plus configuration readbacks.
3. Observe all three DRDY signals, verify approximately 100 Hz per device, verify one XYZ FIFO frame per edge after settling, and quantify missing edges, queue overruns, FIFO overflow and host latency during logging/network access.
4. Run a stationary record to check signed values, clipping, gravity orientation and usable noise floor; record the result without applying a startup offset to stored raw data.
5. Compare a known vibration-frequency input with each sensor/axis and the offline analysis. Record reference instrument, mounting, uncertainty and errors; a synthetic FFT test alone does not establish device accuracy.
6. Exercise a full 600-second run, export/replay its raw file, and confirm the saved counts, timing, window eligibility, summary and storage behavior.

The user plans to prototype the firmware before GPT 6 Astra researches and produces the KiCad schematic/PCB. GPT 6.1 Sol's BOM task follows the agreed hardware design. Keep this map as an input to that work; final components, pads, power circuit, USB-C CC/ESD network, layout and electrical checks remain for that stage.
