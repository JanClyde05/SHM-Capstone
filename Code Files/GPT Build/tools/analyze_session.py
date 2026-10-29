"""Decode SHMRAW2 logs and independently reproduce FFT/window/session results.

python analyze_session.py raw.bin --summary summary.json --output offline.json
Optional --windows windows.csv compares stored firmware bins/flags with NumPy.
Uses no resampling, interpolation, magnitude-of-XYZ, or nominal-rate substitution.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import struct
import zlib
import numpy as np
from reference_math import analyze_axis, estimate_rate, traffic_group

HEADER = struct.Struct("<8sIIQII")
RECORD_DTYPE = np.dtype([
    ("timestamp_us", "<u8"), ("read_timestamp_us", "<u8"),
    ("sample_index", "<u4"), ("scan_cycle_id", "<u4"),
    ("x", "<i2"), ("y", "<i2"), ("z", "<i2"),
    ("sensor_id", "u1"), ("flags", "u1"),
])
assert HEADER.size == 32 and RECORD_DTYPE.itemsize == 32


def load_raw(path: Path):
    data = path.read_bytes()
    if len(data) < HEADER.size:
        raise ValueError("Truncated raw header")
    magic, version, record_size, start_us, duration_s, sensors = HEADER.unpack_from(data)
    if magic != b"SHMRAW2\0" or version != 2 or record_size != 32 or sensors != 3 or duration_s != 600:
        raise ValueError("Unsupported raw schema/header")
    payload = data[HEADER.size:]
    if len(payload) % record_size:
        raise ValueError("Truncated raw record")
    records = np.frombuffer(payload, dtype=RECORD_DTYPE)
    return {"start_us": start_us, "session_s": duration_s,
            "crc32_hex": f"{zlib.crc32(payload) & 0xffffffff:08x}"}, records


def analyze(raw_path: Path, meta: dict, windows_path: Path | None = None):
    header, records = load_raw(raw_path)
    settings = meta["settings"]
    required = ("nominal_fs_hz", "window_s", "session_s", "band_lo_hz", "band_hi_hz",
                "timing_tolerance_us", "fs_tol_fraction")
    for key in required:
        if key not in settings or not math.isfinite(float(settings[key])):
            raise ValueError(f"Missing/invalid setting: {key}")
    if settings["session_s"] != 600 or settings["window_s"] != 60:
        raise ValueError("Approved protocol requires 600 s session and 60 s windows")
    nominal = float(settings["nominal_fs_hz"])
    tolerance = float(settings["timing_tolerance_us"])
    rate_tolerance = float(settings["fs_tol_fraction"])
    clip_limit = float(settings.get("clip_raw_limit", 32000))
    tie_relative = float(settings.get("relative_tie_tolerance", 1e-4))
    if (nominal <= 0 or tolerance < 0 or not 0 <= rate_tolerance < 1 or clip_limit <= 0
            or not math.isfinite(tie_relative) or not 0 <= tie_relative < 1):
        raise ValueError("Invalid acquisition settings")
    start = int(header["start_us"])
    if int(meta["start_us"]) != start:
        raise ValueError("Metadata/header start time mismatch")
    expected_crc = str(meta["raw_crc32_hex"]).lower().removeprefix("0x").zfill(8)
    if header["crc32_hex"] != expected_crc:
        raise ValueError("Raw CRC32 does not match metadata")
    issues = []
    if not meta.get("technical_valid", False): issues.append("DEVICE_REPORTED_TECHNICAL_ISSUE")
    if "record_count" in meta and int(meta["record_count"]) != records.size: issues.append("METADATA_RECORD_COUNT")
    if records.size == 0: issues.append("EMPTY_RAW")
    if np.any((records["sensor_id"] < 1) | (records["sensor_id"] > 3)):
        raise ValueError("Invalid sensor ID")
    if np.any(records["flags"] != 0): issues.append("RECORD_FLAGS_NONZERO")
    if np.any(records["read_timestamp_us"] < records["timestamp_us"]): issues.append("READ_PRECEDES_SAMPLE")
    if records.size > 1:
        # Integer comparisons avoid uint64 subtraction wrap on corrupt order.
        if np.any(records["read_timestamp_us"][1:] < records["read_timestamp_us"][:-1]):
            issues.append("READ_CHRONOLOGY")
        same = records["scan_cycle_id"][1:] == records["scan_cycle_id"][:-1]
        if np.any(same & (records["sensor_id"][1:] <= records["sensor_id"][:-1])):
            issues.append("POLL_ORDER")
    end = start + 600_000_000
    if np.any(records["timestamp_us"] < start) or np.any(records["timestamp_us"] >= end):
        issues.append("SAMPLE_OUTSIDE_SESSION")
    window_results, session_results = [], []
    for sensor in range(1, 4):
        stream = records[records["sensor_id"] == sensor]
        if not stream.size: issues.append(f"S{sensor}_EMPTY")
        if stream.size > 1:
            if np.any(stream["timestamp_us"][1:] <= stream["timestamp_us"][:-1]): issues.append(f"S{sensor}_CHRONOLOGY")
            # uint32 rollover permitted; time and session count still checked.
            index_diff = np.diff(stream["sample_index"].astype(np.uint64)) & 0xffffffff
            if np.any(index_diff != 1): issues.append(f"S{sensor}_SAMPLE_INDEX_GAP")
        valid_peaks = {axis: [] for axis in "xyz"}
        for window in range(10):
            first = start + window * 60_000_000
            selected = stream[(stream["timestamp_us"] >= first) & (stream["timestamp_us"] < first + 60_000_000)]
            n = int(selected.size)
            timestamps = selected["timestamp_us"]
            fs = estimate_rate(n, int(timestamps[0]), int(timestamps[-1])) if n >= 2 else math.nan
            chronology = n >= 2 and bool(np.all(timestamps[1:] > timestamps[:-1]))
            local_index_continuity = n >= 2 and bool(np.all((np.diff(selected["sample_index"].astype(np.uint64)) & 0xffffffff) == 1))
            intervals = np.diff(timestamps.astype(np.int64))
            estimated_period = (int(timestamps[-1]) - int(timestamps[0])) / (n - 1) if n >= 2 else math.nan
            max_jitter = float(np.max(np.abs(intervals - estimated_period))) if intervals.size else None
            boundary_valid = (n >= 2 and int(timestamps[0]) - first <= 2 * estimated_period
                              and first + 60_000_000 - int(timestamps[-1]) <= 2 * estimated_period)
            count_valid = nominal * 60 * (1 - rate_tolerance) - 2 <= n <= nominal * 60 * (1 + rate_tolerance) + 2
            timing_valid = (chronology and local_index_continuity and math.isfinite(fs) and abs(fs / nominal - 1) <= rate_tolerance
                            and max_jitter <= tolerance and boundary_valid and count_valid
                            and bool(np.all(selected["flags"] == 0)))
            if not timing_valid: issues.append(f"S{sensor}_W{window}_TIMING")
            for axis in "xyz":
                result, _ = analyze_axis(selected[axis], fs, float(settings["band_lo_hz"]), float(settings["band_hi_hz"]), tie_relative=tie_relative, clip_abs=clip_limit)
                result.update(window_index=window, sensor_id=sensor, axis=axis,
                              timing_valid=bool(timing_valid), max_interval_error_us=max_jitter,
                              first_us=int(timestamps[0]) if n else None,
                              last_us=int(timestamps[-1]) if n else None)
                if result["status"] == "CLIPPED_INPUT": issues.append(f"S{sensor}_W{window}_{axis}_CLIP")
                if result["valid"] and timing_valid: valid_peaks[axis].append(result["frequency_hz"])
                window_results.append(result)
        for axis in "xyz":
            values = valid_peaks[axis]
            # EQ-MEDIAN-01; root policy all ten windows, not a significance test.
            session_results.append({"sensor_id": sensor, "axis": axis, "valid_windows": len(values),
                                    "median_hz": float(np.median(values)) if len(values) == 10 else None})
    group = None
    if (meta.get("vehicle_count") is not None and settings.get("cutoff1") is not None
            and settings.get("cutoff2") is not None and int(settings["cutoff1"]) < int(settings["cutoff2"])):
        group = traffic_group(int(meta["vehicle_count"]), int(settings["cutoff1"]), int(settings["cutoff2"]))
    comparisons = []
    missing_firmware_windows = []
    if windows_path is not None:
        reference = {(w["window_index"], w["sensor_id"], w["axis"]): w for w in window_results}
        seen = set()
        def parse_bool(value):
            if str(value).lower() in ("1", "true"): return True
            if str(value).lower() in ("0", "false"): return False
            raise ValueError(f"Invalid CSV Boolean: {value}")
        with windows_path.open(newline="", encoding="utf-8-sig") as file:
            for stored in csv.DictReader(file):
                key = int(stored["window_index"]), int(stored["sensor_id"]), stored["axis"].lower()
                if key not in reference: raise ValueError(f"Unexpected firmware window: {key}")
                if key in seen: raise ValueError(f"Duplicate firmware window: {key}")
                seen.add(key)
                offline = reference[key]
                has_peak = bool(offline["valid"] and offline["timing_valid"])
                comparison = {"window_index": key[0], "sensor_id": key[1], "axis": key[2],
                              "sample_count_match": int(stored["sample_count"]) == offline["n"],
                              "valid_peak_match": parse_bool(stored["valid_peak"]) == has_peak,
                              "timing_valid_match": parse_bool(stored["timing_valid"]) == offline["timing_valid"],
                              "bin_match": int(stored["peak_bin"]) == offline["peak_bin"] if has_peak and stored["peak_bin"] else None,
                              "near_tie": offline["near_tie"],
                              "frequency_difference_hz": float(stored["frequency_hz"]) - offline["frequency_hz"] if has_peak and stored["frequency_hz"] else None}
                comparisons.append(comparison)
        missing_firmware_windows = [{"window_index": k[0], "sensor_id": k[1], "axis": k[2]} for k in sorted(set(reference) - seen)]
    # Replace NaN with JSON null; never emit nonstandard JSON numeric literals.
    result = {"session_id": meta.get("session_id"), "mode": meta.get("mode"), "config_hash": meta.get("config_hash"),
              "station_id": meta.get("station_id"), "orientation": meta.get("orientation"),
              "raw_crc32_hex": header["crc32_hex"], "record_count": int(records.size),
              "technical_valid_offline": not issues, "technical_issues": sorted(set(issues)),
              "traffic_group_from_count": group, "vehicle_rate_per_minute": None if meta.get("vehicle_count") is None else meta["vehicle_count"] / 10,
              "streams": session_results, "windows": window_results, "firmware_comparisons": comparisons,
              "missing_firmware_windows": missing_firmware_windows,
              "note": "Numerical reproduction only; not hardware calibration or bridge-mode identification"}
    return sanitize(result)


def sanitize(value):
    if isinstance(value, dict): return {k: sanitize(v) for k, v in value.items()}
    if isinstance(value, list): return [sanitize(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--windows", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    meta = json.loads(args.summary.read_text(encoding="utf-8-sig"))
    result = analyze(args.raw, meta, args.windows)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Decoded {result['record_count']} records, {len(result['windows'])} axis-windows; technical_valid_offline={result['technical_valid_offline']}")
    if result["technical_issues"]: print("Technical issues:", ", ".join(result["technical_issues"]))


if __name__ == "__main__": main()
