"""Small synthetic input checks for pilot cutoff and campaign context workflow."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from derive_traffic_cutoffs import derive


def main():
    pilots = [dict(session_id=f"P{i}", mode="pilot", finalized=True, aborted=False,
                   duration_s=600, vehicle_count=count, station_id="station-A",
                   orientation="X along roadway", technical_valid=True)
              for i, count in enumerate([0, 1, 2, 3, 4, 5])]
    result = derive(pilots)
    assert (result["cutoff1"], result["cutoff2"]) == (1, 3)
    assert result["group_counts"] == {"NEAR_ZERO": 2, "MEDIUM": 2, "HEAVY": 2}
    rejected = 0
    invalid = [
        [dict(p, vehicle_count=1) for p in pilots],
        [dict(p, vehicle_count=count) for p, count in zip(pilots[:3], [0, 1, 1])],
        pilots + [pilots[0]],
    ]
    for field, value in [("mode", "formal"), ("finalized", False), ("duration_s", 599),
                         ("vehicle_count", None), ("vehicle_count", 2.5), ("vehicle_count", True),
                         ("station_id", "station-B"), ("orientation", "rotated")]:
        invalid.append([dict(pilots[0], **{field: value})] + pilots[1:])
    for summaries in invalid:
        try: derive(summaries)
        except ValueError: rejected += 1
        else: raise AssertionError("Invalid pilot summary accepted")
    qc_rejected = [dict(pilots[0], technical_valid=False)] + pilots[1:]
    assert derive(qc_rejected)["observations"][0]["technical_valid"] is False
    try: derive(qc_rejected, require_technical_valid=True)
    except ValueError: rejected += 1
    else: raise AssertionError("Required technical QC ignored")
    # Execute the actual campaign command with equal hashes but different mounts.
    with tempfile.TemporaryDirectory(prefix="shm_traffic_checks_") as directory:
        base = Path(directory)
        first = dict(session_id="S1", mode="formal", technical_valid_offline=True,
                     traffic_group_from_count="MEDIUM", config_hash="same-hash",
                     station_id="station-A", orientation="X along roadway",
                     streams=[dict(sensor_id=1, axis="x", median_hz=3)])
        paths = [base / "one.json", base / "two.json"]
        paths[0].write_text(json.dumps(first), encoding="utf-8")
        campaign = Path(__file__).with_name("analyze_campaign.py")
        for changed in (dict(station_id="station-B"), dict(orientation="rotated")):
            second = dict(first, session_id="S2", **changed)
            paths[1].write_text(json.dumps(second), encoding="utf-8")
            run = subprocess.run([sys.executable, str(campaign), "--output", str(base / "campaign.json"), *map(str, paths)], capture_output=True, text=True)
            assert run.returncode != 0 and "different stations or board orientations" in run.stderr
        paths[1].write_text(json.dumps(dict(first, session_id="S2")), encoding="utf-8")
        subprocess.run([sys.executable, str(campaign), "--output", str(base / "campaign.json"), *map(str, paths)], check=True, capture_output=True, text=True)
        assert json.loads((base / "campaign.json").read_text())["groups"][0]["n"] == 2
    print(f"PASS: known tertiles and optional QC; {rejected} invalid pilot cases rejected; matching campaign accepted and mixed station/orientation rejected")


if __name__ == "__main__": main()
