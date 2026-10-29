# Current research alignment

The user approved paper v2 on2026-10-24. The estimator decision is resolved: mean removal + symmetric Hann + exact N-point FFT magnitude peak on a positive in-band bin, per channel-axis. Ten60s windows per600s session; session median, per-group/channel/axis mean/sampleSD baseline and separate2SD review band.

See APPROVED_METHOD.md for the implementation traceability and MATHEMATICAL_ALGORITHMS.md for the equation audit. Older open-FFT-versus-Welch gates are superseded. Implementation does not establish field validity; use IMPLEMENTATION_STATUS.md for actual checks and remaining bench work.
