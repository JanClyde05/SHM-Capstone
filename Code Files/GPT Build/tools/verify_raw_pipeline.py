"""Synthetic SHMRAW2 fixture checks; never represents a hardware recording."""
import json
from pathlib import Path
import struct
import tempfile
import zlib
import numpy as np
from analyze_session import analyze, HEADER, RECORD_DTYPE


def main():
    start = 1_000_000
    n = 60_000
    raw = np.zeros(n * 3, dtype=RECORD_DTYPE)
    for sensor in (1, 2, 3):
        selected = raw[sensor - 1::3]
        selected["timestamp_us"] = start + np.arange(n, dtype=np.uint64) * 10000 + sensor * 500
        selected["read_timestamp_us"] = selected["timestamp_us"] + 100
        selected["sample_index"] = np.arange(n, dtype=np.uint32)
        selected["scan_cycle_id"] = np.arange(n, dtype=np.uint32)
        selected["sensor_id"] = sensor
        t = np.arange(n) / 100
        for axis, offset in zip("xyz", (0, 1, 2)):
            selected[axis] = np.rint(16000 + 800 * np.sin(2 * np.pi * (1 + 2 * sensor + offset) * t)).astype("<i2")
    with tempfile.TemporaryDirectory(prefix="shm_raw_pipeline_") as temp:
        path = Path(temp) / "synthetic_raw.bin"
        payload = raw.tobytes()
        path.write_bytes(HEADER.pack(b"SHMRAW2\0", 2, 32, start, 600, 3) + payload)
        meta = {"session_id": "SYNTHETIC_ONLY", "mode": "formal", "config_hash": "synthetic-only",
                "start_us": start, "technical_valid": True, "vehicle_count": 2,
                "raw_crc32_hex": f"{zlib.crc32(payload) & 0xffffffff:08x}",
                "settings": {"nominal_fs_hz": 100, "window_s": 60, "session_s": 600,
                             "band_lo_hz": .5, "band_hi_hz": 20, "timing_tolerance_us": 500,
                             "fs_tol_fraction": .03, "cutoff1": 1, "cutoff2": 3}}
        result = analyze(path, meta)
        assert result["record_count"] == 180000
        assert result["technical_valid_offline"], result["technical_issues"]
        assert len(result["windows"]) == 90
        assert result["traffic_group_from_count"] == "MEDIUM"
        assert not result["windows"][0]["near_tie"]
        meta["settings"]["relative_tie_tolerance"] = .75
        diagnostic = analyze(path, meta)
        assert diagnostic["windows"][0]["near_tie"]
        assert diagnostic["streams"] == result["streams"]
        meta["settings"]["relative_tie_tolerance"] = 1
        try: analyze(path, meta)
        except ValueError: pass
        else: raise AssertionError("Invalid metadata tie tolerance accepted")
        meta["settings"]["relative_tie_tolerance"] = 1e-4
        for stream in result["streams"]:
            expected = 1 + 2 * stream["sensor_id"] + "xyz".index(stream["axis"])
            assert stream["valid_windows"] == 10
            assert abs(stream["median_hz"] - expected) < 1e-12, (stream, expected)
        bad_crc = dict(meta, raw_crc32_hex="00000000")
        try: analyze(path, bad_crc)
        except ValueError as e: assert "CRC32" in str(e)
        else: raise AssertionError("CRC mismatch accepted")
        changed = raw.copy()
        changed[3000]["timestamp_us"] += 700
        changed_payload = changed.tobytes()
        path.write_bytes(HEADER.pack(b"SHMRAW2\0", 2, 32, start, 600, 3) + changed_payload)
        meta["raw_crc32_hex"] = f"{zlib.crc32(changed_payload) & 0xffffffff:08x}"
        result = analyze(path, meta)
        assert not result["technical_valid_offline"]
        assert "S1_W0_TIMING" in result["technical_issues"]
        assert result["streams"][0]["valid_windows"] == 9 and result["streams"][0]["median_hz"] is None
        changed = raw.copy()
        changed["sample_index"][3000::3] += 1
        changed_payload = changed.tobytes()
        path.write_bytes(HEADER.pack(b"SHMRAW2\0", 2, 32, start, 600, 3) + changed_payload)
        meta["raw_crc32_hex"] = f"{zlib.crc32(changed_payload) & 0xffffffff:08x}"
        result = analyze(path, meta)
        assert "S1_SAMPLE_INDEX_GAP" in result["technical_issues"]
        assert "S1_W0_TIMING" in result["technical_issues"]
        assert result["streams"][0]["valid_windows"] == 9
        meta["mode"] = "pilot"
        meta["settings"]["cutoff1"] = meta["settings"]["cutoff2"] = 0
        result = analyze(path, meta)
        assert result["traffic_group_from_count"] is None
        # Ensure all output is strict interoperable JSON, including invalid windows.
        json.dumps(result, allow_nan=False)
    print("PASS: synthetic 180000-record/90-axis-window pipeline; CRC corruption, jitter and index gap detected; ten-window median and unclassified pilot checked")


if __name__ == "__main__": main()
