"""Cross-check real compiled C++ against an independent NumPy float64 DFT.

python verify_math.py --native path/to/native_math_check.exe [--report result.json]
No MCU, sensor, sampling accuracy, or frequency calibration is verified here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from reference_math import analyze_axis, pilot_cutoffs, traffic_group


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    executable = str(args.native.resolve())
    subprocess.run([executable, "--selfcheck"], check=True)
    rng = np.random.default_rng(20261024)
    cases = []
    # Different lengths exercise prime, power-of-two, composite, and real-window N.
    for n in (31, 64, 257, 6000, 6001, 6200):
        t = np.arange(n) / 99.73
        x = 16384 + 2000 * np.sin(2 * np.pi * 3.257 * t) + 600 * np.cos(2 * np.pi * 12.73 * t) + rng.normal(0, 40, n)
        cases.append((f"mixed_dc_noise_N{n}", x, 99.73, .5, 20., 0, True))
    n = 6000; t = np.arange(n) / 100
    cases += [
        ("bin_center_3Hz_DC", 16000 + 1500 * np.sin(2 * np.pi * 3 * t), 100., .5, 20., 0, True),
        ("off_grid_3_257Hz", 900 * np.sin(2 * np.pi * 3.257 * t), 100., .5, 20., 0, True),
        ("in_band_over_strong_out_of_band", 10 * np.sin(2 * np.pi * 3 * t) + 1000 * np.sin(2 * np.pi * 30 * t), 100., .5, 20., 0, True),
        ("band_edge_is_diagnostic", np.sin(2 * np.pi * .5 * t), 100., .5, 20., 0, True),
        ("equal_peaks_flag", np.sin(2 * np.pi * 3 * t) + np.sin(2 * np.pi * 8 * t), 100., .5, 20., 0, False),
        ("constant", np.full(n, 16384), 100., .5, 20., 0, True),
        ("clipped", np.full(n, 32767), 100., .5, 20., 32000, True),
        ("nonfinite", np.r_[np.nan, np.zeros(n-1)], 100., .5, 20., 0, True),
        ("nyquist_band_invalid", np.ones(n), 100., .5, 50., 0, True),
        ("no_bin", np.sin(2 * np.pi * 3 * t), 100., 3.001, 3.002, 0, True),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="shm_math_") as temporary:
        directory = Path(temporary)
        for label, samples, fs, lo, hi, clip, compare_bin in cases:
            samples = np.asarray(samples, dtype="<f4")
            input_path, output_path = directory / "input.f32", directory / "spectrum.c64"
            samples.tofile(input_path)
            cpp = json.loads(subprocess.check_output([executable, str(input_path), str(samples.size), str(fs), str(lo), str(hi), str(output_path), str(clip)], text=True))
            expected, spectrum = analyze_axis(samples, fs, lo, hi, clip_abs=clip)
            assert cpp["status"] == expected["status"], (label, cpp, expected)
            normalized_error = None
            if cpp["valid"]:
                if compare_bin:
                    assert cpp["peak_bin"] == expected["peak_bin"], (label, cpp, expected)
                else:
                    assert cpp["near_tie"] and expected["near_tie"], (label, cpp, expected)
                assert cpp["band_edge_peak"] == expected["band_edge_peak"], (label, cpp, expected)
                native_spectrum = np.fromfile(output_path, dtype="<c8")
                normalized_error = float(np.max(np.abs(native_spectrum - spectrum)) / max(1, np.max(np.abs(spectrum))))
                assert normalized_error < 2e-6, (label, normalized_error)
                if label == "bin_center_3Hz_DC": assert cpp["peak_bin"] == 180
                if label == "band_edge_is_diagnostic": assert cpp["band_edge_peak"]
            results.append({"case": label, "status": cpp["status"], "normalized_max_complex_error": normalized_error})
            print(label, cpp["status"], "error", normalized_error)
    assert pilot_cutoffs([0, 1, 2, 3, 4, 5]) == (1, 3)
    assert [traffic_group(c, 1, 3) for c in (0, 1, 2, 3, 4)] == ["NEAR_ZERO", "NEAR_ZERO", "MEDIUM", "MEDIUM", "HEAVY"]
    try: pilot_cutoffs([1, 1, 1, 1, 1, 1])
    except ValueError: pass
    else: raise AssertionError("collapsed pilot groups accepted")
    base = Path(__file__).resolve().parent.parent
    sources = [base / "firmware" / "SHM_Capstone" / name for name in ("dsp.h", "dsp.cpp", "baseline.h", "baseline.cpp")]
    sources += [Path(__file__).resolve(), base / "tools" / "reference_math.py", base / "tools" / "native_math_check.cpp"]
    report = {"verified_at_utc": datetime.now(timezone.utc).isoformat(),
              "numpy_version": np.__version__, "native_executable": executable,
              "seed": 20261024, "normalized_complex_error_tolerance": 2e-6,
              "source_sha256": {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
              "cases": results, "passed": len(results),
              "scope": "Native numerical implementation only; no hardware/field measurement"}
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(results)} C++/NumPy cases and scalar, baseline, traffic checks")


if __name__ == "__main__": main()
