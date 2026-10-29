"""Descriptive statistics over one median per session/group/sensor/axis.

python analyze_campaign.py --output campaign.json offline_session_*.json
Inputs must be analyze_session.py outputs. No inferential test or power claim.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from reference_math import summarize_sessions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sessions", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--review-k", type=float, default=2)
    args = parser.parse_args()
    groups, identifiers, excluded = defaultdict(list), set(), []
    config_hash = None
    context = None
    for path in args.sessions:
        data = json.loads(path.read_text(encoding="utf-8"))
        session_id = data.get("session_id")
        if not session_id or session_id in identifiers:
            raise ValueError("Missing/duplicate session ID; a field session is one observation")
        identifiers.add(session_id)
        if data.get("mode") != "formal" or not data.get("technical_valid_offline") or not data.get("traffic_group_from_count"):
            excluded.append({"session_id": session_id, "reason": "Not formal, technical QC issue, or frozen traffic category missing"})
            continue
        if not data.get("config_hash"): raise ValueError("Missing analysis configuration hash")
        station, orientation = data.get("station_id"), data.get("orientation")
        if not isinstance(station, str) or not station.strip() or not isinstance(orientation, str) or not orientation.strip():
            raise ValueError("Station and orientation are required; regenerate older offline outputs from raw + summary")
        if context is not None and context != (station, orientation):
            raise ValueError("Cannot combine different stations or board orientations into one baseline")
        context = station, orientation
        if config_hash is not None and data["config_hash"] != config_hash:
            raise ValueError("Cannot combine different settings into one baseline")
        config_hash = data["config_hash"]
        for stream in data["streams"]:
            if stream["median_hz"] is None:
                excluded.append({"session_id": session_id, "sensor_id": stream["sensor_id"], "axis": stream["axis"], "reason": "No ten-window median"})
                continue
            key = data["traffic_group_from_count"], stream["sensor_id"], stream["axis"]
            groups[key].append(stream["median_hz"])
    output = {"config_hash": config_hash, "station_id": context[0] if context else None,
              "orientation": context[1] if context else None,
              "groups": [dict(traffic_group=k[0], sensor_id=k[1], axis=k[2], **summarize_sessions(v, args.review_k)) for k, v in sorted(groups.items())],
              "excluded": excluded, "note": "Descriptive session statistics; five-session target is practical, not a power calculation; review band is heuristic"}
    args.output.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(groups)} group/channel/axis summaries")


if __name__ == "__main__": main()
