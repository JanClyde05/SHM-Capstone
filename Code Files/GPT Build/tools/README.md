# Offline analysis and mathematical verification

Use Python 3 with NumPy (`python -m pip install numpy` in your chosen environment). These tools run on the PC, not the ESP32 or Arduino IDE. Start with `../docs/MATHEMATICAL_ALGORITHMS.md` for equations, input units, handling rules, sources and actual checks. `../docs/ASTRA_REVIEW_BRIEF.md` gives GPT6 Astra the independent audit scope, navigation and reproduction commands.

| File | Purpose |
|---|---|
| `reference_math.py` | Independent float64 NumPy FFT and batch statistics; not a translation of embedded Bluestein. |
| `analyze_session.py` | Exact SHMRAW2 binary decoder, payload CRC32/chronology/timing checks, 90 channel-axis windows, ten-window medians and optional firmware-bin comparison. |
| `analyze_campaign.py` | Descriptive statistics over accepted formal sessions; rejects duplicate IDs and mixed settings/stations/orientations. |
| `derive_traffic_cutoffs.py` | Derive nearest-rank count cutoffs from actual finalized 600-second pilot summaries; rejects collapsed or empty groups. |
| `native_math_check.cpp` | Host C++ driver and scalar/baseline checks linked to the actual firmware numerical modules. |
| `verify_math.py` | Generate known/noisy/invalid signals, execute compiled C++, compare entire complex spectra with NumPy. |
| `verify_raw_pipeline.py` | Generate a synthetic 600-second three-stream binary fixture; check decoding, medians, CRC corruption and timing disturbance. |
| `verify_traffic_workflow.py` | Known pilot counts/ties/input validation and campaign station/orientation separation checks. |

Run from this directory, supplying exported files:

```powershell
python analyze_session.py raw.bin --summary summary.json --windows windows.csv --output offline_session.json
python analyze_campaign.py --output campaign.json offline_session_1.json offline_session_2.json
python derive_traffic_cutoffs.py --output pilot_cutoffs.json pilot1_summary.json pilot2_summary.json pilot3_summary.json pilot4_summary.json pilot5_summary.json pilot6_summary.json
python verify_raw_pipeline.py
python verify_traffic_workflow.py
```

`--windows` is optional. Results include bin/frequency differences rather than silently asserting agreement. Inspect any mismatch and near-tie flag. No bridge-mode identity, accuracy calibration, statistical power, or field result is established by these scripts. Pilot observations never enter the campaign's formal baseline.

For pilot cutoffs, supply your actual exported `summary.json` files renamed to distinct file names. All inputs must be finalized pilot sessions of 600 seconds, from the same station and orientation, with distinct IDs and integer vehicle tallies. Add `--require-technical-valid` to require accepted device QC as well; otherwise count observations can be retained even when vibration QC was rejected, and that status is recorded. This option never permits an aborted or shorter count interval. Enter the resulting `cutoff1` and `cutoff2` into the dashboard's freeze form before formal collection. If ties leave a group empty, collect/revise the pilot rather than invent thresholds or tune them to the frequency results.

For native checks, compile outside the sketch folder. Example from a Visual Studio x64 Native Tools prompt (or equivalent g++ compiler):

```bat
cl /nologo /EHsc /std:c++17 /O2 /W4 native_math_check.cpp ..\firmware\SHM_Capstone\dsp.cpp ..\firmware\SHM_Capstone\baseline.cpp /Fe:native_math_check.exe
```

```sh
g++ -std=c++17 -O2 -Wall -Wextra native_math_check.cpp ../firmware/SHM_Capstone/dsp.cpp ../firmware/SHM_Capstone/baseline.cpp -o native_math_check
```

Then execute (use the correct platform-specific executable path):

```powershell
python verify_math.py --native ./native_math_check.exe --report ../reports/math_verification.json
```

The Windows/MSVC command was actually run on 2026-10-24. The g++ alternative is documented for portability and was not run in that session. Keep generated executables/objects in temporary build folders. Never upload these PC tooling files to the Arduino sketch.
