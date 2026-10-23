# Graphs — Architecture & Dependency Maps (Graphify)

> Stage 07 | ICM L2 Contract  
> **Input**: Entire codebase structure  
> **Output**: Mermaid diagrams renderable in Obsidian graph view

## 1. System Architecture Graph

```mermaid
graph TB
    subgraph Hardware["⚡ Hardware Layer"]
        IMU0["MPU6050 #0<br/>X-axis"]
        IMU1["MPU6050 #1<br/>Y-axis"]
        IMU2["MPU6050 #2<br/>Z-axis"]
        I2C["I2C Bus<br/>400kHz"]
        ESP["ESP32-S3<br/>Dual Core"]
    end

    subgraph Backend["🔧 Signal Processing"]
        CALIB["CalibState<br/>Offset Removal"]
        MAF["MafState<br/>Moving Average"]
        MAG["Magnitude<br/>|a|−1g"]
        RMS["computeRMS()"]
        FFT["computeFFT()<br/>Hamming + Peak"]
        INT["computeIntensity()<br/>Normalize 0-1"]
    end

    subgraph Frontend["🖥️ Visualization"]
        POLL["fetch@20Hz<br/>/data endpoint"]
        LPF["Stage 1 LPF<br/>α=0.10"]
        LERP["Stage 2 LERP<br/>Per-frame"]
        VS["Vertex Shader<br/>Marinacci Ripple"]
        FS["Fragment Shader<br/>Heat Ramp"]
        UI["UI/HUD<br/>Table + Alerts"]
    end

    IMU0 & IMU1 & IMU2 --> I2C --> ESP
    ESP --> CALIB --> MAF --> MAG --> RMS & FFT
    RMS --> INT
    FFT --> INT
    INT --> POLL --> LPF --> LERP --> VS --> FS --> UI
```

## 2. File Dependency Graph

```mermaid
graph LR
    MAIN["SHM_Main.ino<br/>Entry Point"]
    CALC["Calculations.h<br/>DSP Library"]
    WEB["WebServerUI.h<br/>HTML/CSS/JS"]
    THREE["three.min.js<br/>Three.js r128"]
    CSV["shm.csv<br/>LittleFS Log"]

    MAIN -->|"#include"| CALC
    MAIN -->|"#include"| WEB
    MAIN -->|serves| CSV
    WEB -->|"script src"| THREE
    MAIN -->|"handleRoot()"| WEB
    MAIN -->|"handleData()"| CSV

    style MAIN fill:#0d1117,stroke:#00e5ff,color:#00e5ff
    style CALC fill:#0d1117,stroke:#00e676,color:#00e676
    style WEB fill:#0d1117,stroke:#ffb300,color:#ffb300
    style THREE fill:#0d1117,stroke:#a0cce0,color:#a0cce0
    style CSV fill:#0d1117,stroke:#ff3d3d,color:#ff3d3d
```

## 3. FreeRTOS Task Interaction Graph

```mermaid
graph TB
    subgraph Core0["Core 0"]
        T1["SensorAcquisition<br/>Priority 3 | 6ms"]
    end

    subgraph Core1["Core 1"]
        T2["Processing<br/>Priority 2 | 50ms"]
        T3["WebServer<br/>Priority 1 | 50ms"]
    end

    subgraph SharedState["Shared State"]
        NODES["gNodes[3]<br/>SensorNode structs"]
        RMSBUF["gRmsBuf[3][50]"]
        FFTBUF["gFftBuf[3][128]"]
        CSVF["gCsvFile<br/>LittleFS"]
    end

    T1 -->|"write (gDataMutex)"| NODES
    T1 -->|"write"| RMSBUF & FFTBUF
    T1 -->|"write (gFileMutex)"| CSVF
    T2 -->|"read"| RMSBUF & FFTBUF
    T2 -->|"write (gDataMutex)"| NODES
    T3 -->|"read (gDataMutex)"| NODES
    T3 -->|"read (gFileMutex)"| CSVF

    style T1 fill:#1a0033,stroke:#00e5ff,color:#00e5ff
    style T2 fill:#1a0033,stroke:#00e676,color:#00e676
    style T3 fill:#1a0033,stroke:#ffb300,color:#ffb300
```

## 4. Signal Processing Pipeline (Detailed)

```mermaid
flowchart LR
    A["Raw I2C<br/>14 bytes"] --> B["readMPU6050()<br/>Unit Conversion"]
    B --> C["calibApply()<br/>−offset"]
    C --> D["mafUpdate() ×3<br/>Per-axis smooth"]
    D --> E["Magnitude<br/>√(x²+y²+z²)−1"]
    E --> F["gRmsBuf<br/>Sliding Window"]
    E --> G["gFftBuf<br/>128 samples"]
    F --> H["computeRMS()<br/>√(Σx²/N)"]
    G --> I["computeFFT()<br/>Hamming→Peak Hz"]
    H --> J["computeIntensity()<br/>RMS/0.3"]
    I --> K["freq (Hz)"]
    J --> L["intensity 0-1"]
    K & L --> M["JSON /data"]

    style A fill:#0d1117,stroke:#ff3d3d,color:#ff3d3d
    style M fill:#0d1117,stroke:#00e676,color:#00e676
```

## 5. Shader Pipeline Graph

```mermaid
flowchart TB
    U["Uniforms<br/>uTime, uAmp0-2, uSpd0-2"] --> VS["Vertex Shader"]
    VS --> RD["ripDisp() ×3<br/>Per-source displacement"]
    VS --> RG["ripGrad() ×3<br/>Analytical normals"]
    RD --> TOTAL["totalDisp = r0+r1+r2"]
    RG --> NORM["worldNormal"]
    TOTAL --> HEAT["vHeat = 0.5+0.5×norm"]
    TOTAL --> POS["displaced position"]

    HEAT --> FS["Fragment Shader"]
    NORM --> FS
    POS --> FS
    FS --> RAMP["heatRamp(t)<br/>5-stop palette"]
    FS --> LIGHT["Phong Lighting<br/>3 lights + specular"]
    FS --> GLOW["Crest Glow + Trough Shadow"]
    RAMP & LIGHT & GLOW --> OUT["gl_FragColor"]

    style U fill:#0d1117,stroke:#00e5ff,color:#00e5ff
    style OUT fill:#0d1117,stroke:#ff3d3d,color:#ff3d3d
```

## 6. Repository Structure Map

```mermaid
graph TB
    ROOT["SHM-Capstone/"]
    CODE["Code Files/"]
    REF["Reference File<br/>(OLD Version)/"]
    ESP["SHM-ESP32-System/"]
    FW["firmware/"]
    DATA["data/"]
    IMG["images/"]
    GER["gerber/"]
    DOC["Documents/"]
    PIC["Pictures/"]
    PRES["Presentations/"]

    ROOT --> CODE & DOC & PIC & PRES
    CODE --> REF --> ESP
    ESP --> FW & DATA & IMG & GER
    FW --> F1["SHM_Main.ino"] & F2["Calculations.h"] & F3["WebServerUI.h"]
    DATA --> D1["three.min.js"] & D2["littlefs-upload.vsix"]

    style ROOT fill:#0d1117,stroke:#00e5ff,color:#00e5ff
    style FW fill:#0d1117,stroke:#00e676,color:#00e676
```

## Links

- [[01-system-overview]] — architecture context
- [[02-signal-processing]] — DSP pipeline detail
- [[03-visualization]] — shader detail
- [[04-firmware]] — task detail
