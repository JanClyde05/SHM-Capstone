"""Derive local nearest-rank traffic tertiles from actual finalized pilot summaries.

python derive_traffic_cutoffs.py --output pilot_cutoffs.json pilot1.json pilot2.json ...
Optional --require-technical-valid requires accepted device QC for every input.
No fabricated counts, frequency-dependent tuning, or universal thresholds.
"""
import argparse
import json
import math
from pathlib import Path


def derive(summaries, require_technical_valid=False):
    observations = []
    identifiers = set()
    context = None
    for summary in summaries:
        identifier = summary.get("session_id")
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError("Pilot session IDs must be present and distinct")
        identifiers.add(identifier)
        if summary.get("mode") != "pilot" or summary.get("finalized") is not True:
            raise ValueError(f"{identifier}: only finalized pilot summaries are eligible")
        duration = summary.get("duration_s")
        if type(duration) not in (int, float) or duration != 600 or summary.get("aborted", False):
            raise ValueError(f"{identifier}: require a complete 600-second pilot session")
        count = summary.get("vehicle_count")
        if type(count) is not int or count < 0:
            raise ValueError(f"{identifier}: vehicle_count must be a nonnegative JSON integer")
        station, orientation = summary.get("station_id"), summary.get("orientation")
        if (
            not isinstance(station, str)
            or not station.strip()
            or not isinstance(orientation, str)
            or not orientation.strip()
        ):
            raise ValueError(f"{identifier}: station and orientation are required")
        if context is not None and context != (station, orientation):
            raise ValueError("Do not mix different stations or board orientations")
        context = station, orientation
        if require_technical_valid and summary.get("technical_valid") is not True:
            raise ValueError(f"{identifier}: device technical QC was not accepted")
        observations.append({
            "session_id": identifier,
            "vehicle_count": count,
            "technical_valid": summary.get("technical_valid") is True,
        })
    if not observations:
        raise ValueError("Supply at least one finalized pilot summary")
    counts = sorted(o["vehicle_count"] for o in observations)
    m = len(counts)
    # EQ-TRAFFIC-02: one-based nearest ranks, converted to zero-based indices.
    rank1, rank2 = math.ceil(m / 3), math.ceil(2 * m / 3)
    c1, c2 = counts[rank1 - 1], counts[rank2 - 1]
    if c1 >= c2:
        raise ValueError("Pilot ties collapse cutoffs; extend/revise the pilot before freezing")
    group_counts = {
        "NEAR_ZERO": sum(c <= c1 for c in counts),
        "MEDIUM": sum(c1 < c <= c2 for c in counts),
        "HEAVY": sum(c > c2 for c in counts),
    }
    if any(n == 0 for n in group_counts.values()):
        raise ValueError("An empty pilot group remains; extend/revise the pilot before freezing")
    return {
        "method": "EQ-TRAFFIC-02 nearest-rank empirical tertiles of 600-second pilot counts",
        "station_id": context[0],
        "orientation": context[1],
        "session_s": 600,
        "pilot_sessions": m,
        "sorted_counts": counts,
        "rank1_one_based": rank1,
        "rank2_one_based": rank2,
        "cutoff1": c1,
        "cutoff2": c2,
        "group_counts": group_counts,
        "require_technical_valid": require_technical_valid,
        "observations": observations,
        "note": "Study-local count groups. Freeze before formal frequency collection; NEAR_ZERO can contain nonzero counts.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summaries", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--require-technical-valid", action="store_true")
    args = parser.parse_args()
    summaries = [json.loads(path.read_text(encoding="utf-8-sig")) for path in args.summaries]
    output = derive(summaries, args.require_technical_valid)
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        f"Pilot cutoffs: cutoff1={output['cutoff1']}, cutoff2={output['cutoff2']}; {output['group_counts']}"
    )


if __name__ == "__main__":
    main()

