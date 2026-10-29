# Firmware data flow

```mermaid
flowchart TD
 IMU[Three independent MPU6050 FIFOs] -->|read XYZ 1 then2 then3| ACQ[Core1 acquisition task]
 IRQ[Three DRDY GPIO interrupt queues] --> ACQ
 ACQ --> RAW[Append-only whole-session PSRAM buffer]
 RAW -->|sealed60-second ranges| DSP[Core0 worker: mean / Hann / exact FFT / peak]
 DSP --> WIN[90 window results]
 WIN --> MED[Per-stream median of ten valid windows]
 RAW -->|capture ends / pause sensors| FS[LittleFS raw / windows / summary]
 MED --> FS
 COUNT[Observer tally + frozen cutoffs] --> FIN[Finalize count and traffic group]
 FS --> FIN
 FIN --> BASE[Matching formal session baseline]
 BASE --> HTTP[HTTP REST + embedded UI]
 ACQ -->|real XYZ preview| HTTP
 DSP -->|latest window peaks| HTTP
```

Sampling and web requests do not share an acquisition loop. No disk writes or downloads occur during capture/processing. The worker reads only sealed immutable raw records; append may continue beyond its published end index. At most ten jobs queue. Whole-session memory remains until all jobs and persistence complete.

acquisitionSuspend/resume stops the read task and sensor/FIFO/IRQ stream before idle flash writes and reinitializes before precheck/session use. No capture may span this reset. Each formal session gets its own config snapshot and exact global600s interval. A fresh10s precheck is required after persistence or config changes.

Core1 acquisition priority18; DSP core0 priority1; Arduino loop/web core1 priority1. These are scheduling choices requiring runtime validation with Wi-Fi enabled. Numerical host tests cannot establish queue timing, flash reliability or sensor measurement accuracy.
