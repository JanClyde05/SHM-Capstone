#pragma once
#include <Arduino.h>

// Active offline assets; compiled into flash. data/ is an inactive scaffold snapshot.
static const char SHM_INDEX_HTML[] PROGMEM = R"SHM_UI(<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#09090b">
  <meta name="color-scheme" content="dark">
  <title>Structural Frequency Monitor</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="app-shell">
    <header class="topbar">
      <a class="brand" href="#live" aria-label="Structural Frequency Monitor home">
        <span class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 40 40" fill="none">
            <path d="M5 29h30M8 29V14l12-7 12 7v15M13 29V18h14v11M17 18v11m6-11v11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 21h7l3-5 4 10 4-8 3 3h11" stroke="#60a5fa" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span class="brand-copy">
          <strong>STRUCTURAL FREQUENCY</strong>
          <small>BUNTUN BRIDGE · LOCAL NODE</small>
        </span>
      </a>

      <div class="topbar-right">
        <span id="nodeStatus" class="connection-pill is-offline" role="status" aria-live="polite">
          <span class="status-dot" aria-hidden="true"></span>
          <span id="nodeStatusText">NODE DISCONNECTED</span>
        </span>
        <span class="header-divider" aria-hidden="true"></span>
        <span class="revision-label">FIRMWARE <b id="firmwareVersion">—</b></span>
      </div>
    </header>

    <nav class="main-nav" aria-label="Main navigation">
      <button class="nav-button is-active" type="button" data-view="live" aria-current="page">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h4l2.2-6 4.6 12 2.2-6H21"/></svg>
        <span>LIVE</span>
      </button>
      <button class="nav-button" type="button" data-view="sessions">
        <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="5" width="16" height="15" rx="2"/><path d="M8 3v4m8-4v4M4 10h16M8 14h3m2 0h3"/></svg>
        <span>SESSION</span>
      </button>
      <button class="nav-button" type="button" data-view="data">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19V5m0 14h15M8 16l3-4 3 2 5-7"/></svg>
        <span>RECORDS</span>
      </button>
      <button class="nav-button" type="button" data-view="baseline">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 18h16M6 15V9m4 6V5m4 10v-4m4 4V7"/></svg>
        <span>BASELINE</span>
      </button>
    </nav>

    <main class="main-content">
      <p id="nodeMessage" class="inline-message node-message" role="status" aria-live="polite">Connect to the node to view readiness.</p>
      <p id="countdownStatus" class="inline-message" role="timer" aria-live="polite"></p>
      <section id="view-live" class="view is-visible" aria-labelledby="liveTitle">
        <div class="page-heading">
          <div>
            <p class="eyebrow">MONITORING NODE <span class="eyebrow-separator">/</span> LIVE VIEW</p>
            <h1 id="liveTitle">Frequency overview</h1>
            <p class="page-description">Independent X/Y/Z measurements from three sensors at one station.</p>
          </div>
          <div class="heading-meta">
            <span class="meta-label">ACQUISITION</span>
            <strong id="acquisitionState" class="mono">AWAITING DATA</strong>
          </div>
        </div>

        <div class="live-grid">
          <section class="panel frequency-panel" aria-labelledby="frequencyTitle">
            <div class="panel-heading">
              <div>
                <p class="eyebrow">MEASURED RESPONSE</p>
                <h2 id="frequencyTitle">Selected sensor frequency</h2>
              </div>
              <select id="sensorSelect" aria-label="Select sensor"><option value="0">SENSOR 01</option><option value="1">SENSOR 02</option><option value="2">SENSOR 03</option></select>
            </div>
            <div class="axis-readouts" aria-live="polite">
              <div class="axis-readout">
                <span class="axis-name">AXIS X</span>
                <strong id="freqX" class="axis-value">—<small> Hz</small></strong>
                <span id="snrX" class="axis-detail">SNR — dB</span>
              </div>
              <div class="axis-readout">
                <span class="axis-name">AXIS Y</span>
                <strong id="freqY" class="axis-value">—<small> Hz</small></strong>
                <span id="snrY" class="axis-detail">SNR — dB</span>
              </div>
              <div class="axis-readout">
                <span class="axis-name">AXIS Z</span>
                <strong id="freqZ" class="axis-value">—<small> Hz</small></strong>
                <span id="snrZ" class="axis-detail">SNR — dB</span>
              </div>
            </div>
            <p class="panel-footnote"><span id="frequencyQuality">NO VALID PEAK</span> · Latest completed analysis window. Axis orientation follows the recorded mounting note.</p>
          </section>

          <section class="panel acquisition-panel" aria-labelledby="acquisitionTitle">
            <div class="panel-heading">
              <div>
                <p class="eyebrow">SENSOR INPUT</p>
                <h2 id="acquisitionTitle">Acquisition status</h2>
              </div>
              <span class="icon-frame" aria-hidden="true">
                <svg viewBox="0 0 24 24"><path d="M12 3v3m0 12v3M3 12h3m12 0h3M6.3 6.3l2.1 2.1m7.2 7.2 2.1 2.1m0-11.4-2.1 2.1m-7.2 7.2-2.1 2.1"/><circle cx="12" cy="12" r="4"/></svg>
              </span>
            </div>
            <div class="sensor-list">
              <div class="sensor-row"><span class="sensor-name"><i class="sensor-indicator" id="sensorDot1"></i>SENSOR 01</span><span class="sensor-value" id="sensorRate1">— Hz</span></div><div id="sensorXyz1" class="raw-values mono">X — · Y — · Z — g</div>
              <div class="sensor-row"><span class="sensor-name"><i class="sensor-indicator" id="sensorDot2"></i>SENSOR 02</span><span class="sensor-value" id="sensorRate2">— Hz</span></div><div id="sensorXyz2" class="raw-values mono">X — · Y — · Z — g</div>
              <div class="sensor-row"><span class="sensor-name"><i class="sensor-indicator" id="sensorDot3"></i>SENSOR 03</span><span class="sensor-value" id="sensorRate3">— Hz</span></div><div id="sensorXyz3" class="raw-values mono">X — · Y — · Z — g</div>
            </div>
            <div class="acquisition-summary">
              <span class="meta-label">MEASURED SAMPLE RATE</span>
              <strong id="sampleRateSummary" class="mono">— Hz</strong>
            </div>
          </section>

          <section class="panel spectrum-panel" aria-labelledby="windowTitle">
            <div class="panel-heading"><div><p class="eyebrow">INDEPENDENT CHANNELS</p><h2 id="windowTitle">Latest window results</h2></div><span id="windowProgress" class="micro-badge">WAITING</span></div>
            <div class="baseline-table-wrap"><table><thead><tr><th>SENSOR</th><th>AXIS</th><th>FREQUENCY</th><th>PEAK CHECK</th></tr></thead><tbody id="channelResults"><tr><td colspan="4" class="empty-cell">WAITING FOR A COMPLETED WINDOW</td></tr></tbody></table></div>
            <p class="panel-footnote">Windows use measured per-sensor sample timing. Detailed QC is retained in the exported records.</p>
          </section>

          <section class="panel live-baseline-panel" aria-labelledby="liveBaselineTitle">
            <div class="panel-heading">
              <div>
                <p class="eyebrow">REFERENCE RANGE</p>
                <h2 id="liveBaselineTitle">Baseline status</h2>
              </div>
            </div>
            <div class="baseline-axis-list">
              <div class="baseline-axis-row"><span>AXIS X</span><span id="baselineStateX" class="baseline-state">NO BASELINE YET</span></div>
              <div class="baseline-axis-row"><span>AXIS Y</span><span id="baselineStateY" class="baseline-state">NO BASELINE YET</span></div>
              <div class="baseline-axis-row"><span>AXIS Z</span><span id="baselineStateZ" class="baseline-state">NO BASELINE YET</span></div>
            </div>
            <p class="panel-footnote">The selected sensor reference is internal to this node and site.</p>
            <button class="text-button" type="button" data-view-link="baseline">VIEW BASELINE DETAILS <span aria-hidden="true">→</span></button>
          </section>

          <section class="panel current-session-panel" aria-labelledby="currentSessionTitle">
            <div class="session-summary-copy">
              <p class="eyebrow">FIELD RECORD</p>
              <h2 id="currentSessionTitle">Current session</h2>
              <p id="currentSessionText" class="muted-copy">No session is active.</p>
            </div>
            <div class="session-summary-meta">
              <span class="meta-label">TRAFFIC LEVEL</span>
              <strong id="currentTrafficLevel" class="mono">—</strong>
            </div>
            <button class="button button-secondary" type="button" data-view-link="sessions">OPEN SESSION</button>
          </section>
        </div>
      </section>

      <section id="view-sessions" class="view" aria-labelledby="sessionPageTitle" hidden>
        <div class="page-heading">
          <div>
            <p class="eyebrow">FIELD RECORD</p>
            <h1 id="sessionPageTitle">Session setup</h1>
            <p class="page-description">Each complete collection session lasts 600 seconds. Tally vehicles concurrently and submit the total after capture.</p>
          </div>
          <span id="sessionPageState" class="micro-badge">NODE DISCONNECTED</span>
        </div>
        <form id="sessionForm" class="panel session-form">
          <div class="form-intro">
            <p class="eyebrow">NEW MEASUREMENT</p>
            <h2>Session details</h2>
            <p class="muted-copy">Keep the sensor in the same position and orientation for the campaign.</p>
          </div>
          <div class="form-grid">
            <label class="form-field"><span>COLLECTION MODE</span><select name="mode" required><option value="pilot">PILOT</option><option value="formal">FORMAL</option></select></label>
            <label class="form-field"><span>STATION ID</span><input name="station_id" maxlength="64" placeholder="Enter the predeclared station ID" required></label>
            <label class="form-field form-field-wide"><span>AXIS ORIENTATION / MOUNTING NOTE</span><input name="orientation" maxlength="128" placeholder="Document X, Y and Z orientation" required></label>
            <label class="form-field">
              <span>OPERATOR</span>
              <input name="operator" maxlength="64" type="text" autocomplete="name" placeholder="Enter operator name" required>
            </label>
            <label class="form-field form-field-wide">
              <span>WEATHER / EVENT NOTES</span>
              <textarea name="notes" maxlength="256" rows="3" placeholder="Enter weather or notable events"></textarea>
            </label>
          </div>
          <div class="form-actions">
            <p class="form-note">Browser time is stored as an epoch mapping. A manually stopped session is incomplete and excluded from formal baselines.</p>
            <div class="button-row">
              <button id="precheckButton" class="button button-secondary" type="button" disabled>RUN PRECHECK</button>
              <button id="startSessionButton" class="button button-primary" type="submit" disabled>START SESSION</button>
              <button id="stopSessionButton" class="button button-outline" type="button" disabled>ABORT CAPTURE</button>
            </div>
          </div>
          <p id="sessionMessage" class="inline-message" role="status" aria-live="polite"></p>
        </form>
        <form id="countForm" class="panel session-form secondary-panel">
          <div class="form-intro"><p class="eyebrow">CONCURRENT TRAFFIC TALLY</p><h2>Complete the field record</h2><p class="muted-copy">Use the total vehicle count observed during this session's 600 seconds. The node classifies the count using frozen cutoffs. After a reboot, find a COUNT PENDING record in Records, enter its session ID here, and submit the tally from your field sheet.</p></div>
          <div class="form-grid"><label class="form-field"><span>SESSION ID</span><input id="countSessionId" name="session_id" maxlength="64" placeholder="Session awaiting count" required></label><label class="form-field"><span>VEHICLES IN 600 SECONDS</span><input name="vehicle_count" type="number" min="0" max="1000000" step="1" placeholder="Enter observed vehicle count" required></label></div>
          <div class="form-actions"><p class="form-note">A pending record is retained until its traffic count is submitted.</p><button id="countButton" class="button button-primary" type="submit" disabled>SAVE VEHICLE COUNT</button></div><p id="countMessage" class="inline-message" role="status"></p>
        </form>
        <form id="freezeForm" class="panel session-form secondary-panel">
          <div class="form-intro"><p class="eyebrow">PILOT DECISIONS</p><h2>Freeze campaign settings</h2><p id="configStatus" class="muted-copy">Configuration unavailable.</p><p class="muted-copy">Set the station ID and axis orientation above, then freeze. Formal sessions must use the same station and orientation.</p></div>
          <div class="form-grid">
            <label class="form-field"><span>LOWER COUNT CUTOFF c1</span><input name="cutoff1" type="number" min="0" step="1" placeholder="Pilot lower tertile" required></label>
            <label class="form-field"><span>UPPER COUNT CUTOFF c2</span><input name="cutoff2" type="number" min="1" step="1" placeholder="Pilot upper tertile" required></label>
            <label class="form-field"><span>BAND LOWER BOUND / Hz</span><input name="band_lo" type="number" min="0.01" max="49" step="0.01" placeholder="Pilot-selected lower bound" required></label>
            <label class="form-field"><span>BAND UPPER BOUND / Hz</span><input name="band_hi" type="number" min="0.02" max="49" step="0.01" placeholder="Pilot-selected upper bound" required></label>
            <label class="form-field"><span>TIMING TOLERANCE / microseconds</span><input name="timing_tolerance_us" type="number" min="50" max="2000" step="1" placeholder="Pilot-selected timing tolerance" required></label>
            <label class="form-field"><span>TYPE FREEZE TO CONFIRM</span><input name="confirm" pattern="FREEZE" maxlength="6" placeholder="FREEZE" required></label>
          </div><div class="form-actions"><p class="form-note">Freeze only after the pilot supports the frequency band, timing QC and distinct traffic groups. Formal capture requires frozen settings.</p><button id="freezeButton" class="button button-secondary" type="submit" disabled>FREEZE SETTINGS</button></div><p id="freezeMessage" class="inline-message" role="status"></p>
        </form>
      </section>

      <section id="view-data" class="view" aria-labelledby="recordsTitle" hidden>
        <div class="page-heading">
          <div>
            <p class="eyebrow">RETAINED MEASUREMENTS</p>
            <h1 id="recordsTitle">Session records</h1>
            <p class="page-description">Download the raw record and summary for offline analysis.</p>
          </div>
          <span id="recordCount" class="micro-badge">0 RECORDS</span>
        </div>
        <section class="panel records-panel" aria-label="Saved session records">
          <div class="records-header"><span>SESSION</span><span>MODE / LEVEL</span><span>STATE</span><span>DURATION</span><span>FILES</span></div>
          <div id="recordsList" class="records-list">
            <p class="empty-state">No saved sessions are available.</p>
          </div>
        </section>
      </section>

      <section id="view-baseline" class="view" aria-labelledby="baselineTitle" hidden>
        <div class="page-heading">
          <div>
            <p class="eyebrow">INTERNAL REFERENCE</p>
            <h1 id="baselineTitle">Baseline summary</h1>
            <p class="page-description">Session-frequency statistics for the selected sensor, by axis and traffic level.</p>
          </div>
          <div class="heading-meta"><select id="baselineSensorSelect" aria-label="Select baseline sensor"><option value="0">SENSOR 01</option><option value="1">SENSOR 02</option><option value="2">SENSOR 03</option></select><span class="micro-badge">MINIMUM 5 ACCEPTED SESSIONS / LEVEL</span></div>
        </div>
        <section class="panel baseline-table-panel" aria-label="Baseline values">
          <div class="baseline-table-wrap">
            <table>
              <thead><tr><th>AXIS</th><th>TRAFFIC LEVEL</th><th>SESSIONS</th><th>MEAN</th><th>SD</th><th>CV</th><th>STATE</th></tr></thead>
              <tbody id="baselineRows"><tr><td colspan="7" class="empty-cell">NO BASELINE YET</td></tr></tbody>
            </table>
          </div>
          <p class="panel-footnote">Mean ± standard deviation is descriptive. The configurable review band is shown after settings are frozen.</p>
        </section>
      </section>

      <footer class="page-footer">
        <span>FREQUENCY MONITORING ONLY</span>
        <span>INTERNAL BASELINE · SINGLE SITE</span>
        <span id="footerHardwareRevision">HARDWARE REVISION —</span>
      </footer>
    </main>
  </div>
  <div id="toast" class="toast" role="status" aria-live="polite"></div>
  <script src="app.js" defer></script>
</body>
</html>
)SHM_UI";

static const char SHM_STYLE_CSS[] PROGMEM = R"SHM_UI(:root {
  color-scheme: dark;
  --bg: #09090b;
  --surface: #121214;
  --surface-raised: #18181b;
  --surface-input: #1f1f23;
  --border: #27272a;
  --border-hover: #3f3f46;
  --text: #fafafa;
  --text-soft: #d4d4d8;
  --muted: #a1a1aa;
  --dim: #71717a;
  --blue: #3b82f6;
  --blue-soft: #60a5fa;
  --green: #10b981;
  --green-soft: #34d399;
  --amber: #f59e0b;
  --amber-soft: #fbbf24;
  --rose: #ef4444;
  --rose-soft: #f87171;
  --font-sans: "Plus Jakarta Sans", Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: "JetBrains Mono", "SF Mono", "Cascadia Code", Consolas, monospace;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;
  --space-7: 48px;
  font-family: var(--font-sans);
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: var(--bg);
  color: var(--text);
}

*, *::before, *::after { box-sizing: border-box; }
html { min-width: 320px; min-height: 100%; background: var(--bg); }
body { min-width: 320px; min-height: 100vh; margin: 0; background: var(--bg); }
button, input, select, textarea { font: inherit; }
button { color: inherit; }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible { outline: 2px solid var(--blue-soft); outline-offset: 3px; }
svg { display: block; }
.mono, .axis-value, .axis-name, .axis-detail, .sensor-value, .micro-badge, .eyebrow, .meta-label, .revision-label, .nav-button, .chart-caption, .chart-axis-labels, .form-field > span, .records-header, .record-level, .record-state, .record-duration, th, .baseline-state, .page-footer { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

.app-shell { width: min(100%, 1600px); min-height: 100vh; margin: 0 auto; padding: 0 var(--space-5); }
.topbar { min-height: 76px; display: flex; align-items: center; justify-content: space-between; gap: var(--space-5); border-bottom: 1px solid var(--border); }
.brand { display: inline-flex; align-items: center; gap: var(--space-3); min-width: 0; color: inherit; text-decoration: none; }
.brand-mark { width: 40px; height: 40px; flex: 0 0 40px; display: grid; place-items: center; border: 1px solid var(--border-hover); border-radius: 50%; background: #000; color: var(--text); }
.brand-mark svg { width: 30px; height: 30px; }
.brand-copy { display: grid; gap: 4px; }
.brand-copy strong { font-size: 13px; font-weight: 900; line-height: 1.1; letter-spacing: -0.025em; }
.brand-copy small { color: var(--muted); font-family: var(--font-mono); font-size: 9px; font-weight: 700; letter-spacing: .08em; }
.topbar-right { display: flex; align-items: center; justify-content: flex-end; gap: var(--space-4); }
.connection-pill { min-height: 36px; display: inline-flex; align-items: center; gap: var(--space-2); padding: 0 var(--space-3); border: 1px solid var(--border); border-radius: 9999px; background: var(--surface-raised); color: var(--muted); font: 700 10px/1 var(--font-mono); letter-spacing: .04em; white-space: nowrap; }
.connection-pill.is-online { border-color: rgba(16,185,129,.38); background: rgba(16,185,129,.09); color: var(--green-soft); }
.connection-pill.is-offline { border-color: rgba(239,68,68,.32); background: rgba(239,68,68,.08); color: var(--rose-soft); }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; flex: 0 0 7px; }
.header-divider { width: 1px; height: 24px; background: var(--border); }
.revision-label { color: var(--muted); font-size: 9px; font-weight: 700; letter-spacing: .04em; white-space: nowrap; }
.revision-label b { margin-left: 4px; color: var(--text-soft); }

.main-nav { min-height: 56px; display: flex; align-items: stretch; gap: var(--space-2); border-bottom: 1px solid var(--border); }
.nav-button { position: relative; min-width: 104px; display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); padding: 0 var(--space-4); border: 0; background: transparent; color: var(--muted); cursor: pointer; font-size: 10px; font-weight: 700; letter-spacing: .06em; }
.nav-button svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.nav-button:hover { color: var(--text); }
.nav-button.is-active { color: var(--text); }
.nav-button.is-active::after { position: absolute; right: var(--space-4); bottom: -1px; left: var(--space-4); height: 2px; background: var(--blue); content: ""; }

.main-content { padding: var(--space-6) 0 var(--space-5); }
.view { display: none; }
.view.is-visible { display: block; }
.page-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: var(--space-5); margin-bottom: var(--space-5); }
.eyebrow { margin: 0 0 var(--space-2); color: var(--muted); font-size: 9px; font-weight: 700; letter-spacing: .1em; line-height: 1.4; }
.eyebrow-separator { padding: 0 var(--space-1); color: var(--dim); }
h1, h2, p { margin-top: 0; }
h1, h2 { color: var(--text); letter-spacing: -.025em; }
h1 { margin-bottom: var(--space-2); font-size: clamp(25px, 3vw, 34px); font-weight: 900; line-height: 1.1; }
h2 { margin-bottom: 0; font-size: 17px; font-weight: 800; line-height: 1.25; }
.page-description, .muted-copy { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.6; }
.heading-meta { display: grid; gap: var(--space-2); justify-items: end; padding-bottom: var(--space-1); }
.meta-label { color: var(--dim); font-size: 9px; font-weight: 700; letter-spacing: .08em; }
.heading-meta strong { font-size: 10px; color: var(--amber-soft); letter-spacing: .04em; }

.live-grid { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: var(--space-4); }
.panel { min-width: 0; padding: var(--space-5); border: 1px solid var(--border); border-radius: 16px; background: var(--surface); }
.frequency-panel { grid-column: span 7; }
.acquisition-panel { grid-column: span 5; }
.spectrum-panel { grid-column: span 8; }
.live-baseline-panel { grid-column: span 4; }
.current-session-panel { grid-column: 1 / -1; display: flex; align-items: center; gap: var(--space-5); }
.panel-heading { min-height: 40px; display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); margin-bottom: var(--space-5); }
.micro-badge { min-height: 28px; display: inline-flex; align-items: center; justify-content: center; flex: 0 0 auto; padding: 0 var(--space-2); border: 1px solid var(--border); border-radius: 9999px; background: var(--surface-raised); color: var(--muted); font-size: 8px; font-weight: 700; letter-spacing: .04em; white-space: nowrap; }
.axis-readouts { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.axis-readout { min-width: 0; display: grid; gap: var(--space-2); padding: 0 var(--space-4); border-left: 1px solid var(--border); }
.axis-readout:first-child { padding-left: 0; border-left: 0; }
.axis-name { display: flex; align-items: center; gap: var(--space-2); color: var(--muted); font-size: 9px; font-weight: 700; letter-spacing: .08em; white-space: nowrap; }
.axis-tag { padding: 3px 5px; border: 1px solid var(--border); border-radius: 4px; color: var(--dim); font-size: 7px; letter-spacing: .03em; }
.axis-value { display: block; color: var(--text); font-size: clamp(22px, 3vw, 34px); font-weight: 700; letter-spacing: -.06em; line-height: 1.1; white-space: nowrap; }
.axis-value small { color: var(--muted); font-size: 11px; font-weight: 500; letter-spacing: 0; }
.axis-detail { color: var(--dim); font-size: 9px; white-space: nowrap; }
.panel-footnote { margin: var(--space-5) 0 0; color: var(--dim); font-size: 11px; line-height: 1.55; }
.icon-frame { width: 36px; height: 36px; display: grid; place-items: center; border: 1px solid var(--border); border-radius: 8px; background: var(--surface-raised); color: var(--blue-soft); }
.icon-frame svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 1.6; stroke-linecap: round; stroke-linejoin: round; }
.sensor-list { display: grid; }
.sensor-row { min-height: 38px; display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); border-bottom: 1px solid var(--border); }
.sensor-row:first-child { border-top: 1px solid var(--border); }
.sensor-name { display: inline-flex; align-items: center; gap: var(--space-2); color: var(--text-soft); font: 700 9px/1 var(--font-mono); letter-spacing: .04em; }
.sensor-indicator { width: 7px; height: 7px; border: 1px solid var(--dim); border-radius: 50%; background: transparent; }
.sensor-indicator.is-present { border-color: var(--green); background: var(--green); }
.sensor-value { color: var(--muted); font-size: 10px; }
.acquisition-summary { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); margin-top: var(--space-4); }
.acquisition-summary strong { color: var(--text); font-size: 11px; }

.spectrum-heading { align-items: center; }
.axis-switch { display: inline-flex; gap: 2px; padding: 3px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg); }
.axis-switch-button { width: 32px; height: 28px; border: 0; border-radius: 5px; background: transparent; color: var(--muted); cursor: pointer; font: 700 10px var(--font-mono); }
.axis-switch-button:hover { color: var(--text); }
.axis-switch-button.is-active { background: var(--surface-raised); color: var(--blue-soft); }
.chart-wrap { position: relative; height: 244px; overflow: hidden; }
#spectrumChart { width: 100%; height: 100%; display: block; }
.chart-empty { position: absolute; inset: 0; display: grid; place-items: center; color: var(--dim); font: 700 9px var(--font-mono); letter-spacing: .12em; pointer-events: none; }
.chart-empty.has-data { display: none; }
.chart-axis-labels { display: flex; justify-content: space-between; margin-top: var(--space-2); color: var(--dim); font-size: 8px; }
.chart-caption { display: flex; justify-content: space-between; gap: var(--space-3); margin-top: var(--space-4); padding-top: var(--space-3); border-top: 1px solid var(--border); color: var(--dim); font-size: 8px; letter-spacing: .04em; }
.baseline-axis-list { display: grid; }
.baseline-axis-row { min-height: 42px; display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); border-bottom: 1px solid var(--border); color: var(--text-soft); font: 700 9px var(--font-mono); }
.baseline-axis-row:first-child { border-top: 1px solid var(--border); }
.baseline-state { color: var(--amber-soft); font-size: 8px; text-align: right; }
.baseline-state.is-valid { color: var(--green-soft); }
.baseline-state.is-review { color: var(--rose-soft); }
.text-button { display: inline-flex; align-items: center; gap: var(--space-2); margin-top: var(--space-4); padding: 0; border: 0; background: transparent; color: var(--blue-soft); cursor: pointer; font: 700 9px var(--font-mono); letter-spacing: .04em; }
.text-button:hover { color: #93c5fd; }
.session-summary-copy { flex: 1 1 auto; }
.session-summary-copy h2 { margin-bottom: var(--space-2); }
.session-summary-meta { min-width: 140px; display: grid; gap: var(--space-2); }
.session-summary-meta strong { color: var(--text-soft); font-size: 10px; }
.button { min-height: 40px; display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2); padding: 0 var(--space-4); border: 1px solid transparent; border-radius: 8px; cursor: pointer; font: 700 9px var(--font-mono); letter-spacing: .05em; white-space: nowrap; transition: background-color .15s ease, border-color .15s ease, color .15s ease; }
.button:disabled { cursor: not-allowed; opacity: .42; }
.button-primary { border-color: #2563eb; background: #2563eb; color: #fff; }
.button-primary:not(:disabled):hover { border-color: #3b82f6; background: #3b82f6; }
.button-secondary { border-color: var(--border-hover); background: var(--surface-raised); color: var(--text-soft); }
.button-secondary:not(:disabled):hover { border-color: #52525b; background: #202024; }
.button-outline { border-color: rgba(239,68,68,.45); background: rgba(239,68,68,.08); color: var(--rose-soft); }
.button-outline:not(:disabled):hover { border-color: var(--rose); background: rgba(239,68,68,.14); }

.session-form { max-width: 920px; }
.form-intro { padding-bottom: var(--space-5); border-bottom: 1px solid var(--border); }
.form-intro h2 { margin-bottom: var(--space-2); }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-5); padding: var(--space-5) 0; }
.form-field { min-width: 0; display: grid; gap: var(--space-2); }
.form-field-wide { grid-column: 1 / -1; }
.form-field > span { color: var(--muted); font-size: 9px; font-weight: 700; letter-spacing: .08em; }
.form-field input, .form-field select, .form-field textarea { width: 100%; min-height: 44px; padding: 0 var(--space-3); border: 1px solid var(--border-hover); border-radius: 8px; background: var(--surface-input); color: var(--text); font-size: 12px; }
.form-field textarea { min-height: 96px; padding: var(--space-3); resize: vertical; }
.form-field input::placeholder, .form-field textarea::placeholder { color: var(--dim); }
.form-field select:invalid { color: var(--dim); }
.form-actions { display: flex; align-items: center; justify-content: space-between; gap: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--border); }
.form-note { max-width: 330px; margin: 0; color: var(--dim); font-size: 11px; line-height: 1.5; }
.button-row { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: var(--space-2); }
.inline-message { min-height: 18px; margin: var(--space-3) 0 0; color: var(--amber-soft); font: 500 10px/1.5 var(--font-mono); }

.records-panel, .baseline-table-panel { padding: 0; overflow: hidden; }
.records-header, .record-row { display: grid; grid-template-columns: minmax(180px, 2fr) minmax(110px, 1fr) minmax(130px, 1fr) minmax(100px, .8fr) minmax(150px, 1.2fr); align-items: center; gap: var(--space-3); padding: 0 var(--space-5); }
.records-header { min-height: 44px; border-bottom: 1px solid var(--border); background: var(--surface-raised); color: var(--muted); font-size: 8px; font-weight: 700; letter-spacing: .08em; }
.record-row { min-height: 58px; border-bottom: 1px solid var(--border); }
.record-row:last-child { border-bottom: 0; }
.record-id { overflow: hidden; color: var(--text-soft); font: 600 10px var(--font-mono); text-overflow: ellipsis; white-space: nowrap; }
.record-level, .record-state, .record-duration { color: var(--muted); font-size: 9px; white-space: nowrap; }
.record-state.is-accepted { color: var(--green-soft); }
.record-links { display: flex; gap: var(--space-3); }
.record-links a { color: var(--blue-soft); font: 700 8px var(--font-mono); text-decoration: none; white-space: nowrap; }
.record-links a:hover { text-decoration: underline; }
.empty-state { margin: 0; padding: var(--space-6) var(--space-5); color: var(--muted); font-size: 12px; text-align: center; }
.baseline-table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th, td { min-width: 92px; padding: var(--space-4); border-bottom: 1px solid var(--border); }
th { background: var(--surface-raised); color: var(--muted); font-size: 8px; font-weight: 700; letter-spacing: .07em; white-space: nowrap; }
td { color: var(--text-soft); font: 500 10px var(--font-mono); white-space: nowrap; }
tbody tr:last-child td { border-bottom: 0; }
.empty-cell { padding: var(--space-6); color: var(--dim); text-align: center; }
.baseline-table-panel .panel-footnote { margin: 0; padding: var(--space-4) var(--space-5); border-top: 1px solid var(--border); }
.table-state { display: inline-flex; min-height: 24px; align-items: center; padding: 0 var(--space-2); border: 1px solid var(--border); border-radius: 9999px; background: var(--surface-raised); color: var(--amber-soft); font: 700 8px var(--font-mono); white-space: nowrap; }
.table-state.is-valid { color: var(--green-soft); }
.table-state.is-review { color: var(--rose-soft); }
.page-footer { display: flex; justify-content: space-between; gap: var(--space-3); margin-top: var(--space-6); padding-top: var(--space-4); border-top: 1px solid var(--border); color: var(--dim); font-size: 8px; letter-spacing: .05em; }
.toast { position: fixed; right: var(--space-5); bottom: var(--space-5); z-index: 9990; max-width: min(420px, calc(100vw - 32px)); padding: var(--space-3) var(--space-4); border: 1px solid var(--border-hover); border-radius: 8px; background: #18181b; color: var(--text); font: 600 10px/1.5 var(--font-mono); opacity: 0; pointer-events: none; transform: translateY(8px); transition: opacity .15s ease, transform .15s ease; }
.toast.is-visible { opacity: 1; transform: translateY(0); }

@media (max-width: 1023px) {
  .frequency-panel, .spectrum-panel { grid-column: span 7; }
  .acquisition-panel, .live-baseline-panel { grid-column: span 5; }
  .axis-readout { padding-right: var(--space-2); padding-left: var(--space-2); }
}
@media (max-width: 720px) {
  .app-shell { padding: 0 var(--space-4); }
  .topbar { min-height: 68px; gap: var(--space-3); }
  .brand-mark { width: 36px; height: 36px; flex-basis: 36px; }
  .brand-copy strong { font-size: 10px; }
  .brand-copy small { font-size: 7px; }
  .topbar-right { gap: var(--space-2); }
  .connection-pill { min-height: 32px; padding: 0 var(--space-2); font-size: 8px; }
  .header-divider, .revision-label { display: none; }
  .main-nav { min-height: 52px; justify-content: space-between; }
  .nav-button { min-width: 0; flex: 1; gap: 6px; padding: 0 var(--space-1); font-size: 8px; }
  .nav-button svg { width: 14px; height: 14px; }
  .nav-button.is-active::after { right: 10px; left: 10px; }
  .main-content { padding-top: var(--space-5); }
  .page-heading { align-items: flex-start; flex-direction: column; gap: var(--space-3); }
  .heading-meta { justify-items: start; }
  .live-grid { grid-template-columns: minmax(0, 1fr); gap: var(--space-3); }
  .frequency-panel, .acquisition-panel, .spectrum-panel, .live-baseline-panel, .current-session-panel { grid-column: 1; }
  .panel { padding: var(--space-4); border-radius: 12px; }
  .axis-readout { gap: var(--space-2); padding: 0 var(--space-2); }
  .axis-name { font-size: 8px; }
  .axis-value { font-size: clamp(21px, 7vw, 30px); }
  .axis-detail { font-size: 8px; }
  .panel-heading { margin-bottom: var(--space-4); }
  .chart-wrap { height: 210px; }
  .chart-caption { flex-wrap: wrap; }
  .current-session-panel { align-items: flex-start; flex-wrap: wrap; gap: var(--space-4); }
  .session-summary-copy { flex-basis: 100%; }
  .session-summary-meta { flex: 1; }
  .form-grid { grid-template-columns: 1fr; gap: var(--space-4); }
  .form-field-wide { grid-column: 1; }
  .form-actions { align-items: flex-start; flex-direction: column; }
  .button-row { width: 100%; justify-content: flex-start; }
  .button-row .button { flex: 1; }
  .records-header { display: none; }
  .record-row { grid-template-columns: minmax(0, 1fr) auto; gap: var(--space-2) var(--space-3); padding: var(--space-3) var(--space-4); }
  .record-id { grid-column: 1 / -1; }
  .record-level, .record-state, .record-duration { font-size: 8px; }
  .record-links { grid-column: 1 / -1; }
  .page-footer { flex-direction: column; gap: var(--space-2); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
}

.raw-values { padding: 0 0 16px; color: var(--blue-soft); font-size: 10px; line-height: 1.5; }
.secondary-panel { margin-top: 24px; }
.secondary-panel .muted-copy { overflow-wrap: anywhere; }
#sensorSelect, #baselineSensorSelect { max-width: 136px; min-height: 36px; padding: 0 8px; border: 1px solid var(--border-hover); border-radius: 8px; background: var(--surface-input); color: var(--text); font: 700 9px var(--font-mono); }
.record-links a[aria-disabled="true"] { color: var(--dim); pointer-events: none; }
.spectrum-panel .baseline-table-wrap { max-height: 360px; }
.baseline-state { white-space: nowrap; }
@media(max-width:720px) { .baseline-axis-row { gap:8px; } .baseline-state { font-size:7px; } }
)SHM_UI";

static const char SHM_APP_JS[] PROGMEM = R"SHM_UI((() => {
  "use strict";
  const axes = ["x", "y", "z"], levels = ["NEAR_ZERO", "MEDIUM", "HEAVY"];
  const model = { connected:false, state:"IDLE", sensor:0, live:null, config:null, baseline:null, busy:false, status:null };
  const el = (id) => document.getElementById(id);
  const finite = (v) => typeof v === "number" && Number.isFinite(v);
  const num = (v, n=3) => finite(v) ? v.toFixed(n) : "—";
  const active = () => ["PRECHECK", "ARMED", "RECORDING", "PROCESSING"].includes(model.state);
  const states = ["NO BASELINE YET", "PROVISIONAL (n<5)", "WITHIN BASELINE", "OUTSIDE BASELINE – REVIEW"];
  const stateMap = {NOT_READY:states[0], PROVISIONAL_BASELINE:states[1], WITHIN_BASELINE:states[2], OUTSIDE_BASELINE_REVIEW:states[3]};
  const assessment = (v) => states.includes(v) ? v : stateMap[v] || states[0];
  async function request(url, values) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 4500);
    try {
      const options = {cache:"no-store", signal:controller.signal};
      if (values) Object.assign(options, {method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded;charset=UTF-8","X-SHM-Request":"local"},body:new URLSearchParams(values)});
      const response = await fetch(url, options), body = await response.json();
      if (!response.ok) throw new Error(body.message || `Request returned ${response.status}`);
      return body;
    } finally { clearTimeout(timer); }
  }
  function controls() {
    el("precheckButton").disabled = !model.connected || active() || model.state === "AWAITING_COUNT";
    const ready=model.status?.hardware_ready!==false && model.status?.psram_ready!==false && model.status?.storage_ready!==false;
    el("startSessionButton").disabled = !model.connected || !ready || model.status?.precheck_ready!==true || active() || model.state === "AWAITING_COUNT";
    el("stopSessionButton").disabled = !model.connected || !["ARMED","RECORDING"].includes(model.state);
    el("countButton").disabled = !model.connected || active();
    el("freezeButton").disabled = !model.connected || active() || model.state === "AWAITING_COUNT" || Boolean(model.config?.frozen);
    document.querySelectorAll(".record-links a").forEach(a => a.setAttribute("aria-disabled",String(active())));
  }
  function connected(value, status) {
    model.connected = value;
    model.status = status || null;
    el("nodeStatus").classList.toggle("is-online", value); el("nodeStatus").classList.toggle("is-offline", !value);
    el("nodeStatusText").textContent = value ? "NODE CONNECTED" : "NODE DISCONNECTED";
    el("sessionPageState").textContent = value ? model.state : "NODE DISCONNECTED";
    el("acquisitionState").textContent = value ? model.state : "AWAITING DATA";
    if (status) {
      el("firmwareVersion").textContent = status.fw_version || "—";
      el("footerHardwareRevision").textContent = `HARDWARE REVISION ${status.hw_rev ?? "—"}`;
      el("nodeMessage").textContent = status.message || `SENSORS ${status.hardware_ready ? "READY" : "NOT READY"} · CAPTURE MEMORY ${status.psram_ready ? "READY" : "NOT READY"} · STORAGE ${status.storage_ready ? "READY" : "NOT READY"}`;
      el("countdownStatus").textContent = model.state === "ARMED" ? `VEHICLE TALLY BEGINS IN ${Math.max(0,Math.min(5,Math.ceil(status.starts_in_s || 0)))} SECONDS` : model.state === "RECORDING" ? `TALLY VEHICLES NOW · ${num(status.elapsed_s,0)} / 600 SECONDS` : "";
    } else {
      el("nodeMessage").textContent = "Node disconnected. Reconnect to view current readiness.";
      el("countdownStatus").textContent = "";
    }
    controls();
  }
  function stateLabel(node, value) {
    const text = assessment(value); node.textContent=text;
    node.classList.toggle("is-valid",text===states[2]); node.classList.toggle("is-review",text===states[3]);
  }
  function availabilityLabel(node, value) {
    if(value === "BASELINE_READY") {node.textContent="BASELINE READY";node.classList.remove("is-valid","is-review");return;}
    stateLabel(node,value);
  }
  function baselineSensor() { return model.baseline?.sensors?.[model.sensor] || model.baseline || {}; }
  function renderLive(data) {
    model.live = data; model.state = data?.state || model.state; controls();
    el("acquisitionState").textContent=data ? model.state : "AWAITING DATA";
    const sensors=data?.sensors || [], selected=sensors[model.sensor] || {};
    const result=selected.axes || data?.axes || {};
    let peaks=0;
    axes.forEach(axis=>{
      const a=result[axis] || {}, valid=a.valid_peak===true; if(valid) peaks++;
      el(`freq${axis.toUpperCase()}`).replaceChildren(document.createTextNode(valid?num(a.f_d_hz):"—"));
      const unit=document.createElement("small"); unit.textContent=" Hz"; el(`freq${axis.toUpperCase()}`).append(unit);
      el(`snr${axis.toUpperCase()}`).textContent=`SNR ${num(a.snr_db,1)} dB`;
      const b=baselineSensor().axes?.[axis] || {};
      stateLabel(el(`baselineState${axis.toUpperCase()}`),a.baseline_state || b.state);
    });
    el("frequencyQuality").textContent=peaks ? `${peaks} AXES WITH PEAK` : "NO VALID PEAK";
    const rates=[];
    for(let i=0;i<3;i++) {
      const s=sensors[i] || {}, rate=s.fs_est_hz ?? data?.fs_est_hz?.[`imu${i+1}`];
      if(finite(rate)&&rate>0) rates.push(rate);
      el(`sensorRate${i+1}`).textContent=`${num(rate,2)} Hz`;
      el(`sensorDot${i+1}`).classList.toggle("is-present",finite(rate)&&rate>0);
      const xyz=model.status?.hardware_ready===false ? [] : s.xyz_g || [];
      el(`sensorXyz${i+1}`).textContent=`X ${num(xyz[0],5)} · Y ${num(xyz[1],5)} · Z ${num(xyz[2],5)} g`;
    }
    el("sampleRateSummary").textContent=rates.length?`${num(Math.min(...rates),2)}–${num(Math.max(...rates),2)} Hz`:"— Hz";
    const id=data?.session_id;
    el("currentSessionText").textContent=id?`${id} · ${model.state} · ${num(data?.elapsed_s ?? model.status?.elapsed_s,0)} s`:"No session is active.";
    el("currentTrafficLevel").textContent=levels.includes(data?.traffic_level)?data.traffic_level.replaceAll("_"," "):"PENDING COUNT";
    if(model.state==="AWAITING_COUNT"&&id) el("countSessionId").value=id;
    const rows=el("channelResults"); rows.replaceChildren();
    if(!sensors.length) { const row=document.createElement("tr"),cell=document.createElement("td");cell.colSpan=4;cell.className="empty-cell";cell.textContent="WAITING FOR A COMPLETED WINDOW";row.append(cell);rows.append(row); }
    sensors.forEach((s,index)=>axes.forEach(axis=>{
      const a=s.axes?.[axis] || {}, row=document.createElement("tr");
      [`SENSOR ${String(index+1).padStart(2,"0")}`,axis.toUpperCase(),a.valid_peak?`${num(a.f_d_hz)} Hz`:"—",a.valid_peak?"VALID PEAK":"NO VALID PEAK"].forEach(v=>{const c=document.createElement("td");c.textContent=v;row.append(c);});rows.append(row);
    }));
    el("windowProgress").textContent=finite(data?.windows_complete)?`${data.windows_complete} / ${data.total_windows || 10} WINDOWS`:"WAITING";
  }
  function renderBaseline(data) {
    model.baseline=data; const body=el("baselineRows");body.replaceChildren();
    const source=baselineSensor().axes || {};
    axes.forEach(axis=>{
      const currentState=model.live?.sensors?.[model.sensor]?.axes?.[axis]?.baseline_state;
      stateLabel(el(`baselineState${axis.toUpperCase()}`),currentState || source[axis]?.state);
      levels.forEach(level=>{
        const a=source[axis]?.levels?.[level] || {}, row=document.createElement("tr");
        [axis.toUpperCase(),level.replaceAll("_"," "),finite(a.n)?String(a.n):"0",`${num(a.mean_hz)} Hz`,`${num(a.sd_hz)} Hz`,`${num(a.cv_pct,1)}%`].forEach(v=>{const c=document.createElement("td");c.textContent=v;row.append(c);});
        const cell=document.createElement("td"),badge=document.createElement("span");badge.className="table-state";availabilityLabel(badge,a.state);cell.append(badge);row.append(cell);body.append(row);
      });
    });
  }
  function renderSessions(data) {
    const sessions=Array.isArray(data)?data:data?.sessions || [],list=el("recordsList");list.replaceChildren();
    el("recordCount").textContent=`${sessions.length} RECORDS`;
    if(!sessions.length) {const p=document.createElement("p");p.className="empty-state";p.textContent="No saved sessions are available.";list.append(p);}
    sessions.forEach(s=>{
      const row=document.createElement("div");row.className="record-row";
      [["record-id",s.session_id || "—"],["record-level",`${String(s.mode || "—").toUpperCase()} / ${s.traffic_level || "PENDING"}`],["record-state",!s.finalized?"COUNT PENDING":s.valid?"QC COMPLETE":"REVIEW QC"],["record-duration",`${num(s.duration_s,0)} s · ${finite(s.vehicle_count)?s.vehicle_count:"—"} vehicles`]].forEach(([cls,val])=>{const span=document.createElement("span");span.className=cls;span.textContent=val;row.append(span);});
      const links=document.createElement("span");links.className="record-links";
      ["raw","summary","windows"].forEach(kind=>{const a=document.createElement("a");a.textContent=kind.toUpperCase();a.href=`/api/sessions/${encodeURIComponent(s.session_id || "")}/${kind}`;a.download="";a.setAttribute("aria-disabled",String(active()));a.addEventListener("click",e=>{if(active())e.preventDefault();});links.append(a);});row.append(links);list.append(row);
    });
  }
  function renderConfig(data) {
    model.config=data;
    el("configStatus").textContent=`${data?.frozen?"FROZEN":"PILOT SETTINGS"} · HASH ${data?.hash || "—"} · BAND ${num(data?.band_lo,2)}–${num(data?.band_hi,2)} Hz · CUTOFFS ${data?.cutoff1 ?? "—"} / ${data?.cutoff2 ?? "—"} · STATION ${data?.station_id || "—"}`;
    if(data?.frozen) {
      const details=el("sessionForm");
      if(!details.elements.station_id.value)details.elements.station_id.value=data.station_id || "";
      if(!details.elements.orientation.value)details.elements.orientation.value=data.orientation || "";
    }
    controls();
  }
  async function refreshExtra() {
    if(active()) return;
    try {renderConfig(await request("/api/config"));}catch{}
    try {renderBaseline(await request("/api/baseline"));}catch{}
    try {renderSessions(await request("/api/sessions"));}catch{}
  }
  async function poll() {
    if(model.busy) return; model.busy=true;
    try {
      const prior=model.state,status=await request("/api/status");model.state=status.state || model.state;connected(true,status);
      renderLive(await request("/api/live"));
      if(prior!==model.state&&!active()) await refreshExtra();
    } catch {connected(false); renderLive(null);} finally {model.busy=false;setTimeout(poll,1000);}
  }
  function showView(name) {
    document.querySelectorAll(".view").forEach(view=>{const yes=view.id===`view-${name}`;view.hidden=!yes;view.classList.toggle("is-visible",yes);});
    document.querySelectorAll("[data-view]").forEach(button=>{const yes=button.dataset.view===name;button.classList.toggle("is-active",yes);if(yes)button.setAttribute("aria-current","page");else button.removeAttribute("aria-current");});
    if(!active()) void refreshExtra();
  }
  async function submit(formId,url,messageId,extra={}) {
    const form=el(formId);if(!form.reportValidity())return;
    const values=Object.fromEntries(new FormData(form));Object.assign(values,extra);
    if(url==="/api/config/freeze") {
      const details=new FormData(el("sessionForm"));
      values.station_id=String(details.get("station_id") || "").trim();values.orientation=String(details.get("orientation") || "").trim();
      if(!values.station_id || !values.orientation) {el(messageId).textContent="Enter the station ID and axis orientation in Session details above before freezing.";return;}
    }
    if(values.station_id!==undefined)values.station_id=String(values.station_id).trim();
    if(values.orientation!==undefined)values.orientation=String(values.orientation).trim();
    if(values.notes!==undefined){values.weather_note=values.notes;delete values.notes;}
    el(messageId).textContent="Submitting…";
    try {
      const response=await request(url,values);el(messageId).textContent=response.message || "Record updated.";
      const status=await request("/api/status");model.state=status.state || model.state;connected(true,status);
      renderLive(await request("/api/live"));await refreshExtra();
    }
    catch(error){el(messageId).textContent=error.message;}
  }
  document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>showView(b.dataset.view)));
  document.querySelectorAll("[data-view-link]").forEach(b=>b.addEventListener("click",()=>showView(b.dataset.viewLink)));
  ["sensorSelect","baselineSensorSelect"].forEach(id=>el(id).addEventListener("change",e=>{model.sensor=Number(e.target.value);el("sensorSelect").value=String(model.sensor);el("baselineSensorSelect").value=String(model.sensor);renderLive(model.live);renderBaseline(model.baseline);}));
  el("sessionForm").addEventListener("submit",e=>{e.preventDefault();void submit("sessionForm","/api/session/start","sessionMessage",{epoch:String(Math.floor(Date.now()/1000))});});
  el("countForm").addEventListener("submit",e=>{e.preventDefault();void submit("countForm","/api/session/finalize","countMessage");});
  el("freezeForm").addEventListener("submit",e=>{e.preventDefault();void submit("freezeForm","/api/config/freeze","freezeMessage");});
  el("precheckButton").addEventListener("click",async()=>{try{const r=await request("/api/session/precheck",{});el("sessionMessage").textContent=r.message || "Precheck requested.";}catch(e){el("sessionMessage").textContent=e.message;}});
  el("stopSessionButton").addEventListener("click",async()=>{if(!window.confirm("Abort this capture? An incomplete run is excluded from formal baselines."))return;try{const r=await request("/api/session/stop",{});el("sessionMessage").textContent=r.message || "Capture stopped.";}catch(e){el("sessionMessage").textContent=e.message;}});
  connected(false);renderLive(null);renderBaseline(null);renderSessions([]);void refreshExtra();void poll();
})();
)SHM_UI";

