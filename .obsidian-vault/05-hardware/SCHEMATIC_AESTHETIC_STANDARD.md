# KiCad Schematic Design Aesthetic Standard & Rules

> **Standard Identifier**: `STD-HW-SCH-001`  
> **Source Reference**: `PCB Files/Reference PCB (OLD Version)/Thesis/Schemstics_SHM.pdf` & `Thesis.kicad_sch`  
> **Author**: Jan Clyde T. Talosig  
> **Target EDA Tool**: KiCad 8.x / 9.x  
> **Purpose**: Codify the schematic visual architecture, eliminate overlapping traces, enforce ERC zero-error safety, and guarantee identical modular aesthetics for all upcoming revisions.

---

## 1. Core Design Philosophy: "Clean Blocks, Zero Crossings"

The reference schematic achieves an exceptionally clean, readable, professional aesthetic by adhering to four fundamental tenets:
1. **Zero Long-Distance Traces**: Signals never cross between major functional areas as raw wires.
2. **Modular Functional Framing**: Circuitry is partitioned into neatly bounded, titled functional zones using visual bus frames.
3. **Stub Wiring + Directional Net Labels**: All inter-block communication is handled via short stub wires and aligned global/net labels.
4. **Strict North-Up / South-Down Polarity**: Positive power rails always point UP, grounds always point DOWN.

---

## 2. Sheet Setup & Geometric Layout

| Parameter | Specification | Purpose / Standard |
| :--- | :--- | :--- |
| **Sheet Size** | A4 Landscape (297 × 210 mm) | Industry standard documentation size |
| **Grid Alignment** | 50 mil (1.27 mm) / 100 mil (2.54 mm) | Strict grid lock ensures symbols snap without misaligned pins |
| **Sheet Margins** | 15 mm – 20 mm clearance | Prevents elements from crowding the sheet frame |
| **Title Block** | Bottom-Right (Zone 5–6 / D) | Title: *"IoT SHM With 3D Analysis Using Three.js"*, Author, Rev, Date |

### The 4-Quadrant Visual Framing System

The schematic is partitioned into 4 distinct bounding boxes using **KiCad Bus lines** (which render with a clean, dark blue / indigo stroke `#000080`):

```
+-----------------------------------------------------------------------------------------+
| [IMU (MPU 6050) AX-AY-AZ]                                                               |
|  +--------------------+      +--------------------+      +--------------------+         |
|  |   IMU Channel 1    |      |   IMU Channel 2    |      |   IMU Channel 3    |         |
|  |     (U2 - X-Axis)  |      |     (U4 - Y-Axis)  |      |     (U5 - Z-Axis)  |         |
|  +--------------------+      +--------------------+      +--------------------+         |
+-----------------------------------------------------------------------------------------+
| [Conns & Regulator]         | [MCU S3 SoC IC]             | [Filters and Boot/RST]      |
|  - USB-C 16-Pin (J1)        |  - ESP32-S3-WROOM-1 (U1)    |  - RC Reset Filter (R1, C5) |
|  - AMS1117-3.3 LDO (U3)     |  - Left: Address Strobe Bus |  - EN Tactile Button (S1)   |
|  - Input/Output Bulk Caps   |  - Right: I2C & USB Stubs   |  - BOOT Button + Damping R2 |
|  - CC1/CC2 5.1k Resistors   |  - Unused GPIOs with (x)    |  - +3V3 Bulk Decoupling     |
+-----------------------------+-----------------------------+-----------------------------+
```

| Block Name | Typical Coordinates (X, Y in mm) | Primary Contents |
| :--- | :--- | :--- |
| **`IMU (MPU 6050) AX-AY-AZ`** | Top Box: `(21.59, 20.32)` to `(275.59, 99.06)` | Triaxial / multi-channel sensor array, pull-ups, local decoupling |
| **`Conns and Regulator`** | Bottom-Left: `(17.78, 113.03)` to `(106.68, 191.77)` | USB-C connector, LDO regulator, power entry, CC pull-downs |
| **`MCU S3 SoC IC`** | Bottom-Center: `(106.68, 113.03)` to `(176.53, 191.77)` | ESP32-S3 SoC, GPIO pinouts, unused pin terminations |
| **`Filters and Boot/RST`** | Bottom-Right: `(176.53, 113.03)` to `(267.97, 191.77)` | EN timing, BOOT circuit, system decoupling capacitors |

---

## 3. Wiring Discipline & Zero-Overlap Rules

### Rule 3.1: Complete Elimination of Spaghetti Wires
- **Strict Prohibition**: No wire may travel across the sheet from one quadrant to another.
- **Enforcement**: Inter-module connectivity is achieved strictly through **Net Labels** (`global_label` or local `label`).

### Rule 3.2: Short Stub Connection Standard
- Component pin wires extend between **2.54 mm (100 mil)** and **10.16 mm (400 mil)** before terminating into a label, component junction, or power symbol.
- Never bend a wire more than once unless forming a local component loop (e.g., bypass capacitor).

### Rule 3.3: Collinear Stub & Label Alignment
- To avoid ragged, messy pin breakouts, all labels attached to a vertical pin column must share the exact same X-coordinate:
  - **ESP32 Left Pin Labels** (`BOOT`, `EN`, `IMU-AD0X1`, `IMU-AD0Y1`, `IMU-AD0Z1`): Left-aligned at `X = 121.92 mm` (`shape=input`, `rot=180°`).
  - **ESP32 Right Pin Labels** (`D-`, `D+`, `IMU-SCL`, `IMU-SDA`): Right-aligned at `X = 152.40 mm` (`shape=input`, `rot=0°`).
  - **USB-C Data Lines**: Aligned at `X = 49.53 mm`.

### Rule 3.4: Label Shape Conventions
- Labels use arrow/flag shapes corresponding to the logical signal direction:
  - Outputs / Controls: Arrow points outward.
  - Inputs / Receivers: Arrow points inward.
  - Bidirectional / Bus lines (SDA/SCL): Diamond or bidirectional flag.

---

## 4. Power & Ground Routing Conventions

### Rule 4.1: North-Up (+3V3, +5V) & South-Down (GND)
- **Positive Power**: Always uses the upright arrow symbol (`+3V3`, `+5V`, `VLOGIC`). It points straight upward (`rot=0°`).
- **Ground (GND)**: Always uses the 3-horizontal-bar GND symbol. It points straight downward (`rot=0°`).
- **Exceptions**: None. Ground symbols are never rotated upside-down or sideways.

### Rule 4.2: Decoupling Capacitor Geometry
- Every IC decoupling capacitor is placed vertically:
  - **Top pin**: Wires directly into the positive power rail (`+3V3` or IC pin).
  - **Bottom pin**: Wires directly to an independent local `GND` symbol.
- **Reference & Value**: Placed alongside the capacitor body, right-justified or left-justified, never colliding with wire stubs.

```
       +3V3
        ▲
        │
      ┌─┴─┐
      │ C │  100nF
      └─┬─┘
        │
       ─┴─ GND
```

---

## 5. Channel Symmetry & Symmetrical Duplication

When designing multi-channel sensor stages (e.g. 3-axis MPU-6050 array):
1. **Exact Pitch Duplication**: Each sensor block is an identical clone translated horizontally by a fixed pitch ($\Delta X \approx 84\text{ mm}$ to $90\text{ mm}$).
2. **Identical Passive Placement**:
   - **Top-Left**: I2C pull-up resistors (4.7k $\Omega$) tied to `+3V3`.
   - **Top-Right**: VDD & VLOGIC decoupling capacitor (100nF) to `+3V3` and `GND`.
   - **Right-Side**: Pin 20 (CPOUT) capacitor (220pF) and Pin 10 (REGOUT) capacitor (100nF) aligned vertically with GND at the bottom.
   - **Bottom-Side**: Pin 18 (GND) and Pin 11 (FSYNC) connected downward to GND.
3. **Address Line Indexing**:
   - Only the address line label changes per channel: `IMU-AD0X1`, `IMU-AD0Y1`, `IMU-AD0Z1`.

---

## 6. Electrical Rules Check (ERC) Integrity Standard

### Rule 6.1: Mandatory No-Connect (`x`) Termination
- Every unused pin on any IC or connector **MUST** have an explicit KiCad No-Connect flag (`x`):
  - ESP32-S3 unused GPIOs: `IO0, IO1, IO2, IO3, IO14, IO15, IO16, IO37, IO38, IO39, IO40, IO41, IO42, IO45, IO46, IO47, IO48`.
  - MPU-6050 unused pins: `INT` (if polling mode), `AUX_DA`, `AUX_CL`.
  - USB-C unused pins: `SBU1, SBU2`.
- **Zero Tolerance**: 0 ERC errors, 0 unconnected pin warnings.

### Rule 6.2: Essential Hardware Protections
- **USB-C Configuration**: Dual $5.1\text{ k}\Omega$ pull-down resistors on CC1 and CC2 to GND (required to request 5V from Type-C power sources).
- **MCU Reset (EN) RC Filter**: $10\text{ k}\Omega$ pull-up to `+3V3` + $1\,\mu\text{F}$ capacitor to GND + $100\text{ nF}$ parallel debounce on reset button S1.
- **MCU Boot Mode Protection**: Series $100\,\Omega$ resistor (R2) on BOOT switch (S2) to prevent ringing during transition into download mode.

---

## 7. Standardized Net Naming Scheme

| Net Category | Standard Naming Format | Examples |
| :--- | :--- | :--- |
| **Power Rails** | `+<VOLTAGE>` | `+5V`, `+3V3` |
| **Ground** | `GND` | `GND` |
| **Shared Sensor Bus** | `<SUBSYSTEM>-<SIGNAL>` | `IMU-SCL`, `IMU-SDA` |
| **Sensor Address Strobe** | `<SUBSYSTEM>-AD0<AXIS><INDEX>` | `IMU-AD0X1`, `IMU-AD0Y1`, `IMU-AD0Z1` |
| **USB Differential** | `D+`, `D-` | `D+`, `D-` |
| **Core Control** | `<SIGNAL_NAME>` | `EN`, `BOOT` |

---

## 8. Typography and Designator Standard

- **Section Titles**: Font size `1.27 mm` (50 mil), Bold/Capitalized, placed at top-left inside bounding box.
- **Component References**: Font size `1.27 mm`, placed top or left of symbol.
- **Component Values**: Font size `1.27 mm`, placed bottom or right of symbol.
- **Standard Value Formatting**:
  - Resistors: `100R`, `4.7K`, `5.1k`, `10k`
  - Capacitors: `220pF`, `100nF`, `1uF`, `10uF`, `22uF`
  - Active ICs: Full part number (`ESP32-S3-WROOM-1`, `MPU-6050`, `AMS1117-3.3`)
