# Prototype bring-up and evidence record

Updated 2026-10-26 from `design/circuit_spec.json`, the firmware hardware interface, and [ELECTRICAL_DECISIONS](ELECTRICAL_DECISIONS.md). **These are procedures and acceptance evidence to collect; no powered-board measurement has been performed here.** Obtain the final CAD/release review before ordering or assembling this work-in-progress design.

## 1. Record the actual specimen

Record board revision and source hashes; fabrication stackup/copper thickness; module marking; all component MPNs and substitutions; sensor pin1 orientation; assembly method; power supply/cable; ambient temperature; instruments/probes and calibration status; firmware version/configuration hash. Photograph both sides. Substitutions require renewed footprint, rating, stability and thermal review.

Use the actual approved schematic for probing. This guide's reference designators correspond to the current circuit specification and must be updated if it changes. Three IMUs are U2=IMU1, U3=IMU2, U4=IMU3; U5 is the AP7361C-33E-13 regulator, U6 is USBLC6-2SC6, J1 is USB-C, J2 is the UART fallback.

## 2. Unpowered assembly inspection

Inspect QFN bridges, open pads, solder balls, misplaced capacitors and connector staking under magnification. Verify the MPU center is not soldered to a PCB land, according to the selected manufacturer layout. Confirm module and regulator pin mapping against the actual purchased part: **AP7361C E-package pin2/tab is ground**, unlike a generic1117 layout. Check the populated fuse and supply path.

Measure and record resistance/continuity between VBUS_USB, +5V_FUSED, +3V3 and GND with the board unpowered. Capacitors and semiconductor junctions affect meter readings; an arbitrary resistance threshold is not proof of correctness. Investigate a persistent near-zero supply short before power. Verify CC1 and CC2 each have a separate approximately5.1kΩ path to GND and are not shorted together.

Verify USB A6/B6 share D+, A7/B7 share D-, and no bridge connects the two. Check that native USB reaches module pads13/14 through R3/R4. Inspect the ESD ground return and regulator tab/thermal vias. Check antenna exclusion and metal clearance against the source ledger; the enclosure and mounting hardware are part of that inspection.

## 3. First power and rail qualification

Use a known nominal5V source with current limiting and adequate capability for the intended load, connected through the USB-C input path. Record the current-limit setting and measured startup waveform rather than treating the fuse hold rating as a device-current specification. Do not simultaneously apply an independent supply through a debug connection. J2 carries GND/TX/RX only; the label `3V3` describes logic level, not a power-output pin.

Measure +3V3 at TP1 relative to TP2 and at each IMU's VDD/VLOGIC local capacitors. Record startup minimum/maximum, rise time, idle/radio load ripple and any brownout/reset. Manufacturer limits and conditions are linked in ELECTRICAL_DECISIONS: MPU VDD2.375–3.46V; VLOGIC1.71V toVDD, including its specified rise requirement. Apply the complete source conditions, not only these abbreviated numbers.

Measure regulator case/board temperature at representative worst intended ambient and radio/capture load until temperatures stabilize. Record input/output voltage and current concurrently. Calculate dissipation from measured values; compare against a justified junction-temperature estimate and the actual PCB thermal construction. The 1A LDO rating is not evidence of acceptable continuous operation. If regulation or thermal limits fail, revise the power design and repeat CAD and bench checks.

## 4. Programming and recovery

Follow `../../Code Files/GPT Build/docs/ARDUINO_IDE_SETUP.md` from this hardware folder's root, or navigate to the firmware project directly. Confirm ESP32-S3, 16MB flash, OPI PSRAM, native USB CDC settings and custom partition configuration. Use a data-capable USB cable and document the exact host/supply connection.

Check normal USB enumeration and a small serial/status interaction before a full acquisition session. If recovery is needed, hold BOOT, operate RESET, then release BOOT according to Espressif's download-mode procedure. The optional J2 path requires a **3.3V logic-level** UART adapter with crossed TX/RX and common GND; it provides no power pin. Confirm actual pin labels before attachment.

Do not format retained research data casually. The firmware has explicit Serial maintenance commands; archive recordings before a requested erase. First-time filesystem preparation should follow the firmware workflow and record the action.

## 5. Sensor and timing qualification

| Signal | Probe / current destination | Expected configuration, not a measured result |
| --- | --- | --- |
| I2C0 SDA/SCL | TP3/TP4; GPIO8/9 | IMU1 at0x68, IMU2 at0x69 |
| I2C1 SDA/SCL | TP5/TP6; GPIO10/11 | IMU3 at0x68 |
| IMU1/2/3 DRDY | TP7/TP8/TP9; GPIO4/5/6 | Separate active-high pulses, nominal100Hz each |
| UART TX/RX | TP10/TP11 and J2 | Diagnostic fallback at3.3V logic |

Scan each bus separately, verify WHO_AM_I=0x68 at all three selected addresses, and retain register readbacks. Scope both I2C buses at the intended400kHz setting. Record rise/fall times, low/high levels, transaction errors and probe loading; the selected2.2kΩ resistors are a design starting value. Check each DRDY pulse train and verify one6-byte acceleration XYZ FIFO frame per edge after settling. Test network access and logging conditions that could delay firmware service.

Do not interpret sequential service as simultaneous conversion. Each MPU has its own clock. Verify that FIFO ordering, DRDY timestamps, sample indices and recorded rates remain consistent, and that lost edges/overflows trigger rejection instead of invented samples. Firmware acceptance rules and the10-second precheck are documented in its HARDWARE_INTERFACE and PROTOTYPE_WORKFLOW files.

## 6. Research recording qualification

Run stationary-noise observations and controlled known-frequency excitation with a documented external reference and mounting method. Record the excitation/reference uncertainty, each sensor-axis response and any board flex effects. Same-frequency agreement between the three onboard ICs is not an external accuracy reference.

Secure the PCB through its intended mounting interface and inspect local support near each sensor. Confirm cable forces, button operation and enclosure mounting do not bend the sensing regions. Establish a repeatable orientation record: all three ICs are triaxial; they are not separate X-only/Y-only/Z-only devices.

Execute a600-second pilot session with ten60-second windows and concurrent traffic tally only after bench suitability is established. Keep power applied until PSRAM capture is persisted. Download raw, summary and window files; run the provided independent offline analysis and compare timing/QC/FFT outputs. Pilot cutoffs must be derived and frozen before formal baseline collection. Do not accept a bench test as proof of bridge safety or a structural diagnosis.

## Evidence table to fill

| Test ID | Date/specimen/config | Instrument and conditions | Measured result | Acceptance source | Pass/fail and corrective action |
| --- | --- | --- | --- | --- | --- |
| P01 assembly and continuity | Pending | Pending | Not measured | Final schematic and manufacturer pin drawings | Pending |
| P02 startup/ripple/load | Pending | Pending | Not measured | Verified supply/reset conditions | Pending |
| P03 thermal | Pending | Pending | Not measured | Regulator and module limits with actual ambient/PCB | Pending |
| P04 USB/recovery | Pending | Pending | Not measured | Espressif USB/download guide and selected host conditions | Pending |
| P05 I2C/DRDY/FIFO | Pending | Pending | Not measured | MPU datasheet/register map and firmware timing contract | Pending |
| P06 mechanical/noise/reference-frequency | Pending | Pending | Not measured | Declared experiment and external reference | Pending |
| P07 complete research-session export | Pending | Pending | Not measured | Approved method and independent analysis | Pending |
