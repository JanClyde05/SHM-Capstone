"""Independent NumPy float64 reference; equation IDs match the firmware audit.

This uses NumPy's FFT, not a translation of the embedded Bluestein routine.
It never turns timing gaps into interpolated samples or replaces missing data.
"""
from __future__ import annotations
import math
import numpy as np


def estimate_rate(count: int, first_us: int, last_us: int) -> float:
    """EQ-RATE-01; times must be true per-sensor sample epochs."""
    if count < 2 or last_us <= first_us:
        return math.nan
    return (count - 1) * 1_000_000 / (last_us - first_us)


def analyze_axis(samples, fs: float, lo: float, hi: float,
                 tie_relative: float = 1e-4, clip_abs: float = 0):
    x = np.asarray(samples, dtype=np.float64)
    result = {"status": "INVALID_PARAMETERS", "valid": False, "frequency_hz": None,
              "n": int(x.size), "fs_hz": fs, "bin_spacing_hz": None,
              "peak_bin": None, "peak_magnitude": None, "near_tie": False,
              "band_edge_peak": False}
    if (x.ndim != 1 or x.size < 4 or not all(map(math.isfinite, (fs, lo, hi, tie_relative, clip_abs)))
            or fs <= 0 or not 0 < lo < hi < fs / 2 or not 0 <= tie_relative < 1 or clip_abs < 0):
        return result, None
    result["bin_spacing_hz"] = fs / x.size  # EQ-BIN-01
    if not np.isfinite(x).all():
        result["status"] = "NONFINITE_INPUT"
        return result, None
    if clip_abs > 0 and np.any(np.abs(x) >= clip_abs):
        result["status"] = "CLIPPED_INPUT"
        return result, None
    centered = x - np.mean(x)  # EQ-MEAN-01
    if not np.any(centered):
        result["status"] = "ZERO_SIGNAL"
        return result, None
    window = .5 - .5 * np.cos(2 * np.pi * np.arange(x.size) / (x.size - 1))  # EQ-HANN-01, symmetric
    spectrum = np.fft.fft(centered * window)  # EQ-DFT-01, independent implementation
    bins = np.arange(1, (x.size - 1) // 2 + 1)
    freqs = bins * (fs / x.size)
    bins = bins[(freqs >= lo) & (freqs <= hi)]
    if bins.size == 0:
        result["status"] = "NO_BAND_BINS"
        return result, spectrum
    magnitudes = np.abs(spectrum[bins])
    if not np.isfinite(magnitudes).all():
        result["status"] = "NUMERICAL_ERROR"
        return result, spectrum
    winner_index = int(np.argmax(magnitudes))  # Ascending bins => lowest exact tie.
    winner = int(bins[winner_index])
    maximum = float(magnitudes[winner_index])
    if maximum <= 0:
        result["status"] = "ZERO_SIGNAL"
        return result, spectrum
    result.update(status="VALID", valid=True, frequency_hz=winner * fs / x.size,
                  peak_bin=winner, peak_magnitude=maximum,
                  near_tie=int(np.count_nonzero(magnitudes >= maximum * (1 - tie_relative))) > 1,
                  band_edge_peak=winner_index in (0, bins.size - 1))
    return result, spectrum


def summarize_sessions(values, review_k: float = 2.0, practical_target: int = 5):
    """EQ-STATS-01, EQ-SD-01, EQ-CV-01, EQ-BAND-01, EQ-BAND-02.

    One value per field session; no inferential interval is produced.
    """
    v = np.asarray(values, dtype=np.float64)
    if v.ndim != 1 or not v.size or not np.isfinite(v).all() or np.any(v <= 0):
        raise ValueError("Session frequencies must be finite and positive")
    if not math.isfinite(review_k) or review_k <= 0 or practical_target < 1:
        raise ValueError("Review multiplier and completion target must be positive")
    mean = float(np.mean(v))
    sd = float(np.std(v, ddof=1)) if v.size >= 2 else None
    return {"n": int(v.size), "mean_hz": mean, "sample_sd_hz": sd,
            "cv_percent": None if sd is None else 100 * sd / mean,
            "descriptive_band_hz": None if sd is None else [mean - sd, mean + sd],
            "review_band_hz": None if sd is None else [mean - review_k * sd, mean + review_k * sd],
            "review_k": review_k, "practical_target_met": v.size >= practical_target}


def pilot_cutoffs(counts):
    """EQ-TRAFFIC-02: nearest-rank empirical tertiles; reject collapsed cutoffs."""
    if not counts or any(type(v) is not int or v < 0 for v in counts):
        raise ValueError("Pilot counts must be nonnegative integers")
    ordered = sorted(counts)
    m = len(ordered)
    c1, c2 = ordered[math.ceil(m / 3) - 1], ordered[math.ceil(2 * m / 3) - 1]
    if not c1 < c2 or max(ordered) <= c2:
        raise ValueError("Ties collapse traffic groups; repeat/revise pilot before freezing")
    return c1, c2


def traffic_group(count: int, c1: int, c2: int) -> str:
    """EQ-TRAFFIC-03: classify from frozen local count boundaries."""
    if any(type(v) is not int or v < 0 for v in (count, c1, c2)) or c1 >= c2:
        raise ValueError("Invalid frozen traffic cutoffs")
    return "NEAR_ZERO" if count <= c1 else "MEDIUM" if count <= c2 else "HEAVY"
