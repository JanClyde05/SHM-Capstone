// Native numerical verification only; not part of the Arduino sketch.
// Compile with dsp.cpp + baseline.cpp. See tools/README.md.
#include "../firmware/SHM_Capstone/dsp.h"
#include "../firmware/SHM_Capstone/baseline.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <vector>

void require(bool condition, const char* message) {
    if (!condition) { std::fprintf(stderr, "CHECK FAILED: %s\n", message); std::exit(1); }
}

void selfCheck() {
    BaselineAccumulator accumulator;
    for (double value : {1., 2., 3., 4., 5.}) require(baselineAccumulate(&accumulator, value), "accumulate");
    BaselineAxisSummary summary;
    require(baselineSummarize(accumulator, &summary), "summary");
    require(summary.n == 5 && summary.meanHz == 3., "session mean/count");
    require(std::abs(summary.sampleSdHz - std::sqrt(2.5)) < 1e-12, "Bessel correction");
    require(std::abs(summary.coefficientVariationPct - 100. * std::sqrt(2.5) / 3.) < 1e-12, "CV");
    require(summary.descriptiveLoHz == 3. - summary.sampleSdHz, "descriptive band");
    require(summary.reviewHiHz == 3. + 2. * summary.sampleSdHz, "review band");
    require(!baselineAccumulate(&accumulator, NAN) && !baselineAccumulate(&accumulator, 0), "invalid data rejection");
    require(accumulator.n == 5, "invalid input cannot update baseline");
    baselineBegin();
    require(baselineAddSession(0, 0, 0, 4), "independent cell add");
    require(baselineGet(0, 0, 0, &summary) && summary.n == 1 && !summary.sdDefined, "n1 spread undefined");
    require(!baselineGet(1, 0, 0, &summary), "group isolation");
    require(!baselineGet(0, 1, 0, &summary), "sensor isolation");
    require(!baselineGet(0, 0, 1, &summary), "axis isolation");
    require(std::abs(dspEstimateRateHz(6000, 10000, 60000000) - 100.) < 1e-12, "N-1 timing intervals");
    require(std::isnan(dspEstimateRateHz(1, 0, 1)), "invalid rate");
    float odd[] = {5, 1, 3}, even[] = {4, 1, 2, 3}; double median;
    require(dspMedian(odd, 3, &median) && median == 3, "odd median");
    require(dspMedian(even, 4, &median) && median == 2.5, "even median");
    require(dspWorkspaceLength(6000) == 16384, "exact N6000 workspace");
    std::puts("Native scalar/baseline checks passed");
}

int main(int argc, char** argv) {
    if (argc == 2 && std::string(argv[1]) == "--selfcheck") { selfCheck(); return 0; }
    if (argc != 8) { std::fprintf(stderr, "usage: native_math_check input.f32 N fs low high spectrum.c64 clipAbs\n"); return 2; }
    const size_t n = size_t(std::strtoull(argv[2], nullptr, 10));
    const double fs = std::strtod(argv[3], nullptr);
    std::vector<float> input(n);
    std::ifstream file(argv[1], std::ios::binary);
    file.read(reinterpret_cast<char*>(input.data()), std::streamsize(n * sizeof(float)));
    require(file.gcount() == std::streamsize(n * sizeof(float)), "fixture bytes");
    size_t m = dspWorkspaceLength(n);
    std::vector<DspComplex> a(m), b(m);
    DspWorkspace workspace = {a.data(), b.data(), m};
    DspSettings settings;
    settings.bandLoHz = std::strtod(argv[4], nullptr); settings.bandHiHz = std::strtod(argv[5], nullptr);
    settings.clipAbs = std::strtod(argv[7], nullptr);
    DspAxisResult result;
    dspAnalyzeAxis(input.data(), n, fs, settings, &workspace, &result);
    std::ofstream spectrum(argv[6], std::ios::binary);
    spectrum.write(reinterpret_cast<char*>(a.data()), std::streamsize(n * sizeof(DspComplex)));
    std::printf("{\"status\":\"%s\",\"valid\":%s,\"peak_bin\":%llu,\"fs_hz\":%.17g,\"bin_spacing_hz\":%.17g,\"peak_magnitude\":%.17g,\"near_tie\":%s,\"band_edge_peak\":%s}\n",
       dspStatusName(result.status), result.validPeak ? "true" : "false",
       static_cast<unsigned long long>(result.peakBin), result.fsEstimateHz,
       result.binSpacingHz, result.peakMagnitude, result.nearTie ? "true" : "false", result.bandEdgePeak ? "true" : "false");
    return 0;
}
