# 07 — References and Links (with verification status)

✅ = opened and read during this review (2026-10-23). 🔗 = well-known URL given from memory; **not opened** — verify before citing in the thesis or relying on a specific value. 📚 = taken from the manuscript's reference list; DOI not re-verified here.

## Datasheets and hardware

| Item | URL | Status | Used for |
|---|---|---|---|
| ESP32-S3-WROOM-1 / -1U Datasheet v1.8 | https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf | ✅ | pin map (Table 3-1), IO35–37 note, strapping pins, current (Table 6-4), EN RC, land pattern |
| ESP32-S3 Hardware Design Guidelines | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/index.html | 🔗 | layout, antenna keep-out |
| ESP32-S3 Series Datasheet / TRM | https://www.espressif.com/en/support/documents/technical-documents | 🔗 | I2C controllers, GPIO matrix |
| MPU-6000/6050 Product Specification Rev 3.4 (mirror) | https://www.mikrocontroller.net/attachment/236856/MPU-6050.pdf | ✅ | typical circuit & BOM (§7.2–7.3), clock accuracy (Table 6.6, §7.15), noise 400 µg/√Hz (Table 6.2), PCB rules (§11.3–11.4), I2C addresses (§9.2) |
| MPU-6000/6050 Register Map | https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Register-Map1.pdf | 🔗 | register addresses/bit fields (**verify every value in `03`**) |
| MPU-6050 TDK product page | https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/ | 🔗 | lifecycle status check |
| AMS1117 datasheet | http://www.advanced-monolithic.com/pdf/ds1117.pdf | 🔗 | dropout, output-capacitor ESR/stability |
| USBLC6-2 (ST) | https://www.st.com/resource/en/datasheet/usblc6-2.pdf | 🔗 | USB ESD |
| GCT USB4105 | https://gct.co (search part) | 🔗 | USB-C receptacle footprint |
| Hirose DM3AT microSD socket | https://www.hirose.com (search part) | 🔗 | SD socket |
| KiCad docs / CLI | https://docs.kicad.org | 🔗 | ERC/DRC, export |

## Software

| Item | URL | Status |
|---|---|---|
| PlatformIO | https://platformio.org | 🔗 |
| Arduino-ESP32 core | https://github.com/espressif/arduino-esp32 | 🔗 |
| ESP-DSP (FFT fc32) | https://github.com/espressif/esp-dsp | 🔗 |
| ESP-IDF programming guide (ESP32-S3) | https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/ | 🔗 |
| ArduinoJson | https://arduinojson.org | 🔗 |
| uPlot (charts) | https://github.com/leeoniya/uPlot | 🔗 |
| SciPy `welch`, `f_oneway`, `kruskal`, `levene`, `shapiro` | https://docs.scipy.org/doc/scipy/reference/stats.html | 🔗 |
| statsmodels (Tukey HSD) | https://www.statsmodels.org | 🔗 |
| scikit-posthocs (Dunn) | https://scikit-posthocs.readthedocs.io | 🔗 |

## Literature that supports design choices (from the manuscript)

| Source | DOI (as in manuscript) | Supports |
|---|---|---|
| Welch (1967) | https://doi.org/10.1109/TAU.1967.1161901 📚 | Welch averaged periodogram |
| Hasani & Freddi (2023) | https://doi.org/10.3390/infrastructures8120172 📚 | OMA, peak picking limits |
| Chen, Omenzetter & Beskhyroun (2017) | https://doi.org/10.1016/j.engstruct.2017.08.066 📚 | peak picking on weak ambient excitation |
| Hidalgo-Fort et al. (2024) | https://doi.org/10.3390/s24155078 📚 | edge-computing SHM node |
| Hasani et al. (2024) | https://doi.org/10.3390/s24072121 📚 | wireless MEMS OMA node |
| Giermann et al. (2025) | https://doi.org/10.3390/s25154543 📚 | low-cost MEMS limitations/field use |
| Komarizadehasl et al. (2022a, b) | https://doi.org/10.3390/s22155725 · https://doi.org/10.3390/s22249808 📚 | low-cost accelerometer bridge monitoring |
| Sohn (2007) | https://doi.org/10.1098/rsta.2006.1935 📚 | environmental/operational variability |
| Zhou & Sun (2019) | https://doi.org/10.1016/j.ymssp.2019.05.063 📚 | traffic/temperature effects |
| Kim et al. (2003) | https://doi.org/10.1007/BF02857543 📚 | vehicle mass effect |
| Chang et al. (2014) | https://doi.org/10.12989/sss.2014.13.5.755 📚 | parked-vehicle effect |

Action for JC: before submission, open every DOI in your reference list and confirm title/authors/year match; strip `?utm_source=chatgpt.com` from the Cornwell (1999) and Welch (1967) links; make sure each listed reference is cited in the text.
