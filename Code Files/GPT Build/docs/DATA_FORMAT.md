# Retained acquisition schema2

Each session directory /S<number>/ contains raw.shmb, windows.csv and summary.json. IDs increment in NVS; existing directories are never reused. A new flash filesystem is formatted only by an explicit Serial command.

raw.shmb is little-endian with a32-byte header: Python struct '<8sIIQII'. Magic bytes SHMRAW2 followed by NUL; schema2; record size32; start_us uint64; nominal session duration600s uint32; sensor count3 uint32.

Each32-byte record is '<QQIIhhhBB': DRDY timestamp_us(uint64), FIFO read_timestamp_us(uint64), per-sensor sample_index(uint32), retrieval scan_cycle_id(uint32), signed X/Y/Z int16, sensor_id1..3(uint8), flags(uint8). Flag bit0 marks any axis abs(raw)>=32000. Counts retain gravity and offsets; no calibration subtraction is applied to raw data.±2g nominal conversion is raw/16384g. Index continues across successful sensor restarts during one MCU boot.

A cycle groups retrieval order1,2,3; it does not assert simultaneous conversions or simultaneous receipt. FIFO read epochs can be delayed and must not be used as sample times. The decoder verifies monotonic sensor epochs/indices and preserves all axes.

Windows use DRDY epochs in half-open [start+w*60s,start+(w+1)*60s). Number of samples may vary with actual sensor clock. fs=(N-1)*1e6/(last-first). QC checks per-sensor index continuity, clipping, measured fs within3% of100Hz, endpoint coverage within2 measured periods, and each interval within the frozen tolerance of that window's mean interval. FIFO/DRDY faults or raw-buffer overflow also invalidate the session. No result is silently repaired or resampled.

windows.csv has90 rows for a completed session (10 windows×3 channels×3 axes). Columns: window_index,sensor_id,axis,sample_count,first_us,last_us,fs_est_hz,bin_spacing_hz,peak_bin,frequency_hz,valid_peak,status,timing_valid,near_tie,band_edge. Undefined frequency cells are empty. No extra missing-frequency row is fabricated.

summary.json retains schema/version/config hash, station/orientation/operator/weather, start monotonic and optional calendar epoch, actual duration, count/group/finalization, technical validity, settings snapshot, raw CRC32 and9 stream session medians/valid-window counts/review states. A null median means fewer than ten valid window estimates. A technical invalidity excludes all stream values from baseline. Pilot data never contribute to formal baseline.

Summary QC is explicit: qc_mask bit0 CLIPPING, bit1 SAMPLE_INDEX_GAP, bit2 WINDOW_TIMING, bit3 OPERATOR_OR_ACQUISITION_ABORT, bit4 RAW_CAPACITY, bit5 ACQUISITION_INTEGRITY, bit6 INCOMPLETE_WINDOW_SET, bit7 PERSISTENCE_INCOMPLETE. qc_reasons lists corresponding strings; acquisition_error preserves the original driver error. These are firmware assertions to examine alongside raw replay, not physical calibration results. settings.relative_tie_tolerance records the near-tie diagnostic tolerance.

After a reboot, a complete stored but unfinalized summary can receive the original observer count by explicit session ID. Finalization uses that retained snapshot's cutoffs and context; already-finalized counts are immutable. No RAM capture or partial file is reconstructed by this operation. A recovered old session is not loaded into live preview buffers.

EQ-CRC-01: CRC32/ISO-HDLC over raw RECORD PAYLOAD ONLY (header excluded), initial0xffffffff, reflected polynomial0xedb88320, finalxor0xffffffff, lower-case8hex raw_crc32_hex. Python zlib.crc32(payload) must agree. CRC detects accidental corruption; it is not authentication.

EQ-HASH-01: SHA256 of the explicit canonical string in session.cpp/configHash. It includes firmware identity, model/map, register/rate/window/FFT choices, band/timing/cutoffs, clipping, valid-window policy and review multiplier. Station and orientation are matched separately for baseline membership. Hashing does not prove settings or data correct.

Capture is RAM first. Power interruption before raw persistence loses the in-progress session. Writes after capture can leave a partial file/directory if power is lost. Never treat a directory without a parseable finalized summary as an accepted baseline record. Text summaries use a temporary file and filesystem rename. A raw file is never overwritten on finalization.

Back up all3 files together. Run tools/analyze_session.py RAW --summary SUMMARY (see tool help). After verifying independent backups, Serial 'PURGE_RAW S<number> CONFIRM' explicitly removes only that node raw file; windows/summary remain for baseline reconstruction. Serial 'FORMAT_ERASE_ALL' removes all filesystem records; use only intentionally. Downloads never remove data.
