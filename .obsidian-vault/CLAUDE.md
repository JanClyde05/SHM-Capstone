# SHM-Capstone — ICM Root Router (L0)

> **Interpretable Context Methodology (ICM)** workspace.  
> Ponytail-optimised: minimal tokens, maximum signal.

## Workspace Map

| Stage | Folder | Purpose |
|-------|--------|---------|
| 01 | `01-system-overview/` | Architecture, pipeline, hardware |
| 02 | `02-signal-processing/` | Calibration, MAF, RMS, FFT, Intensity |
| 03 | `03-visualization/` | WebGL shaders, smoothing, heatmap, UI |
| 04 | `04-firmware/` | FreeRTOS tasks, I2C, CSV logging |
| 05 | `05-hardware/` | PCB, wiring, IMU config |
| 06 | `06-documents/` | Thesis papers, presentations, scripts |
| 07 | `07-graphs/` | Mermaid dependency + architecture graphs |
| 08 | `08-ai-integration/` | OpenRouter, Omniroute config + usage |

## Load Rules

- **Never load all stages simultaneously.** Read only the active stage `CONTEXT.md`.
- Each stage is **≤ 4K tokens** (Ponytail constraint).
- Cross-references use `[[wikilinks]]` — Obsidian resolves automatically.

## AI Routing

- **OpenRouter**: `https://openrouter.ai/api/v1` — multi-model queries against vault
- **Omniroute**: `http://localhost:20128/v1` — local fallback gateway with auto-failover
- See `08-ai-integration/CONTEXT.md` for full config.
