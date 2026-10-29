/*
 * ============================================================
 * websocket_server.cpp  —  v2 (UPDATED)
 *
 * DASHBOARD CHANGES:
 *
 *   FIX ② — Anomaly popup spam
 *     Removed auto-dismiss banner (showAlert / alert-banner).
 *     Replaced with a SIDE TRAY that:
 *       • Slides in from right on first anomaly alert
 *       • Shows all alerts as timestamped log entries
 *       • Has a ✕ Minimize button → collapses to a floating
 *         red badge on the right edge
 *       • Badge shows total unread anomaly count
 *       • Clicking badge reopens the tray
 *       • "Clear All" button inside tray resets the log
 *     Because the firmware now only sends newAnomaly once per
 *     event, the tray only gets one entry per real anomaly,
 *     not one every 2.5 seconds.
 *
 *   FIX ③ — CSV download requires internet
 *     Removed all CDN/network dependencies.
 *     CSV is now generated entirely in-browser from the last
 *     received WebSocket data using Blob + createObjectURL.
 *     Works 100% offline on the ESP32's own WiFi AP.
 *     File is named SHM_Data_YYYY-MM-DDThh-mm-ss.csv
 *
 *   BONUS — Table view
 *     Toggle button switches between Card grid and a data
 *     table (NODE | Ax | Ay | Az | Gx | Gy | Gz | RMS |
 *     FREQ | INTENS% | STATUS), matching the screenshot.
 * ============================================================
 */

#include "websocket_server.h"

static AsyncWebServer s_server(80);
static AsyncWebSocket s_ws(WS_PATH);

static volatile int s_clientCount = 0;
static uint32_t     s_lastCleanup = 0;

// ============================================================
// DASHBOARD HTML  (PROGMEM, no external dependencies)
// ============================================================

static const char DASHBOARD_HTML[] PROGMEM = R"rawhtml(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SHM Bridge Monitor</title>
<style>
/* ── Reset & Base ─────────────────────────────── */
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',Arial,sans-serif;background:#0d1117;
     color:#c9d1d9;min-height:100vh;overflow-x:hidden}

/* ── Header ──────────────────────────────────── */
header{background:#161b22;padding:13px 20px;border-bottom:1px solid #30363d;
       display:flex;align-items:center;justify-content:space-between;
       flex-wrap:wrap;gap:10px;position:sticky;top:0;z-index:100}
.hdr-left h1{font-size:1.1rem;color:#58a6ff;font-weight:700}
.hdr-left p{font-size:.73rem;color:#8b949e;margin-top:2px}
.hdr-right{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.btn{padding:6px 14px;border-radius:6px;font-size:.77rem;font-weight:600;
     cursor:pointer;border:none;transition:opacity .2s}
.btn:hover{opacity:.82}
.btn-blue{background:#1f6feb;color:#fff}
.btn-amber{background:#d29922;color:#0d1117}
.btn-green{background:#238636;color:#fff}
#ws-label{padding:3px 10px;border-radius:12px;font-size:.73rem;font-weight:700}
.lbl-ok{background:#1a3520;color:#3fb950}
.lbl-err{background:#3a1a1a;color:#f85149}
.lbl-wait{background:#2a2215;color:#e3b341}

/* ── Status bar ──────────────────────────────── */
#status-bar{background:#161b22;border-bottom:1px solid #21262d;
            padding:7px 20px;display:flex;gap:20px;font-size:.77rem;
            flex-wrap:wrap;align-items:center}
.stat{color:#8b949e}.stat b{color:#c9d1d9}
#s-anom b{color:#f85149}

/* ── View toggle ─────────────────────────────── */
#view-bar{padding:10px 20px;display:flex;gap:8px;align-items:center}
.vtog{padding:5px 14px;border-radius:6px;font-size:.77rem;font-weight:600;
      cursor:pointer;border:1px solid #30363d;background:#21262d;color:#8b949e}
.vtog.active{background:#1f6feb;color:#fff;border-color:#1f6feb}

/* ── Card grid ───────────────────────────────── */
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));
      gap:11px;padding:0 20px 20px}
.card{background:#161b22;border:1px solid #30363d;border-radius:10px;
      padding:13px;transition:border-color .4s,box-shadow .4s}
.card.anomaly{border-color:#f85149;box-shadow:0 0 16px rgba(248,81,73,.22)}
.card-header{display:flex;justify-content:space-between;align-items:flex-start;
             margin-bottom:9px}
.card-label{font-size:.67rem;color:#8b949e;text-transform:uppercase;
            letter-spacing:.06em}
.card-id{font-size:1rem;color:#58a6ff;font-weight:700;margin-top:2px}
.card.anomaly .card-id{color:#f85149}
.badge{font-size:.64rem;padding:2px 7px;border-radius:8px;font-weight:700}
.b-ok{background:#1a3520;color:#3fb950}
.b-anom{background:#3a1a1a;color:#f85149}
.metrics{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px}
.metric{background:#0d1117;border-radius:6px;padding:6px 8px}
.m-label{font-size:.64rem;color:#8b949e;text-transform:uppercase;
         letter-spacing:.04em}
.m-value{font-size:.85rem;color:#e6edf3;font-weight:500;margin-top:2px}
.acc-row{margin-bottom:9px;background:#0d1117;border-radius:6px;padding:6px 8px}
.heat-label{display:flex;justify-content:space-between;font-size:.69rem;
            color:#8b949e;margin-bottom:4px}
.heatbar{height:7px;border-radius:4px;background:#21262d;overflow:hidden}
.heatfill{height:100%;border-radius:4px;
          transition:width .6s ease,background .6s ease;width:0%}

/* ── Table view ──────────────────────────────── */
#tbl-wrap{display:none;padding:0 20px 20px;overflow-x:auto}
#data-table{width:100%;border-collapse:collapse;font-size:.78rem;
            white-space:nowrap}
#data-table th{background:#161b22;color:#8b949e;font-weight:600;
               text-transform:uppercase;letter-spacing:.05em;
               padding:9px 12px;border-bottom:2px solid #30363d;
               position:sticky;top:44px;text-align:right}
#data-table th:first-child{text-align:left}
#data-table td{padding:8px 12px;border-bottom:1px solid #21262d;
               text-align:right;color:#c9d1d9}
#data-table td:first-child{text-align:left;font-weight:600;color:#58a6ff}
#data-table tr.anom-row td{color:#f85149}
#data-table tr.anom-row td:first-child{color:#f85149}
#data-table tr:hover td{background:#161b22}
.tbl-status{padding:2px 8px;border-radius:8px;font-size:.68rem;font-weight:700}
.ts-ok{background:#1a3520;color:#3fb950}
.ts-anom{background:#3a1a1a;color:#f85149}

/* ── Anomaly Side Tray ───────────────────────── */
#anom-tray{position:fixed;right:0;top:0;bottom:0;width:310px;
           background:#161b22;border-left:2px solid #f85149;
           display:flex;flex-direction:column;
           transform:translateX(100%);
           transition:transform .35s cubic-bezier(.4,0,.2,1);
           z-index:500;box-shadow:-8px 0 32px rgba(0,0,0,.5)}
#anom-tray.open{transform:translateX(0)}
.tray-hdr{background:#2a1010;padding:12px 14px;
          display:flex;align-items:center;gap:8px;
          border-bottom:1px solid #f85149;flex-shrink:0}
.tray-title{flex:1;color:#f85149;font-weight:700;font-size:.85rem;
            letter-spacing:.04em}
#tray-count{background:#f85149;color:#fff;border-radius:10px;
            padding:1px 7px;font-size:.7rem;font-weight:700;
            min-width:20px;text-align:center}
#tray-min-btn{background:none;border:1px solid #8b949e;color:#8b949e;
              cursor:pointer;font-size:.8rem;padding:3px 8px;
              border-radius:5px;transition:all .2s}
#tray-min-btn:hover{color:#c9d1d9;border-color:#c9d1d9}
#tray-body{flex:1;overflow-y:auto;padding:10px;scroll-behavior:smooth}
#tray-body::-webkit-scrollbar{width:4px}
#tray-body::-webkit-scrollbar-thumb{background:#30363d;border-radius:4px}
.tray-entry{background:#0d1117;border:1px solid #30363d;border-radius:7px;
            padding:9px 11px;margin-bottom:8px;border-left:3px solid #f85149}
.te-node{color:#f85149;font-weight:700;font-size:.8rem;margin-bottom:3px}
.te-detail{color:#c9d1d9;font-size:.76rem;line-height:1.5}
.te-time{color:#8b949e;font-size:.68rem;margin-top:4px}
.tray-footer{padding:10px;flex-shrink:0;border-top:1px solid #21262d}
#tray-clear-btn{width:100%;padding:7px;background:#21262d;
                border:1px solid #30363d;border-radius:6px;
                color:#8b949e;cursor:pointer;font-size:.77rem;
                transition:all .2s}
#tray-clear-btn:hover{color:#c9d1d9;border-color:#8b949e;background:#2d333b}
.tray-empty{text-align:center;padding:30px 20px;color:#8b949e;font-size:.8rem}

/* ── Anomaly Badge (minimized) ───────────────── */
#anom-badge{position:fixed;right:0;top:50%;
            transform:translateY(-50%);
            background:#f85149;color:#fff;
            padding:12px 7px;border-radius:8px 0 0 8px;
            cursor:pointer;z-index:499;display:none;
            box-shadow:-3px 0 14px rgba(248,81,73,.45);
            transition:opacity .2s}
#anom-badge:hover{opacity:.85}
.badge-inner{display:flex;flex-direction:column;align-items:center;gap:5px;
             font-size:.7rem;font-weight:700;letter-spacing:.03em}
.badge-icon{font-size:1rem}
.badge-num{background:rgba(0,0,0,.3);border-radius:8px;
           padding:1px 5px;min-width:18px;text-align:center}
</style>
</head>
<body>

<!-- ── Anomaly Side Tray ──────────────────────────────────── -->
<div id="anom-tray">
  <div class="tray-hdr">
    <span class="tray-title">⚠ ANOMALY LOG</span>
    <span id="tray-count">0</span>
    <button id="tray-min-btn" onclick="minimizeTray()">✕ Minimize</button>
  </div>
  <div id="tray-body">
    <div class="tray-empty" id="tray-empty-msg">No anomalies detected.</div>
  </div>
  <div class="tray-footer">
    <button id="tray-clear-btn" onclick="clearAlerts()">🗑 Clear All Alerts</button>
  </div>
</div>

<!-- ── Minimized badge ────────────────────────────────────── -->
<div id="anom-badge" onclick="openTray()">
  <div class="badge-inner">
    <span class="badge-icon">⚠</span>
    <span class="badge-num" id="badge-num">0</span>
  </div>
</div>

<!-- ── Header ────────────────────────────────────────────── -->
<header>
  <div class="hdr-left">
    <h1>🌉 SHM Bridge Monitor</h1>
    <p>ESP32-S3 &nbsp;|&nbsp; 9× MPU6050 &nbsp;|&nbsp; Real-Time Vibration Analysis</p>
  </div>
  <div class="hdr-right">
    <span id="uptime" style="color:#8b949e;font-size:.8rem">00:00:00</span>
    <!-- FIX ③: CSV download uses Blob — no internet required -->
    <button class="btn btn-amber" onclick="downloadCSV()">⬇ Download CSV</button>
    <span id="ws-label" class="lbl-wait">⬤ Connecting</span>
  </div>
</header>

<!-- ── Status bar ────────────────────────────────────────── -->
<div id="status-bar">
  <span class="stat">Nodes: <b id="s-nodes">—</b></span>
  <span class="stat">Rate: <b id="s-rate">— Hz</b></span>
  <span class="stat">Packets: <b id="s-pkt">0</b></span>
  <span class="stat" id="s-anom">Anomalies: <b>0</b></span>
  <span class="stat">Max RMS: <b id="s-maxrms">—</b></span>
  <span class="stat">Max Freq: <b id="s-maxfreq">—</b></span>
  <span class="stat">Heap: <b id="s-heap">—</b></span>
</div>

<!-- ── View toggle ───────────────────────────────────────── -->
<div id="view-bar">
  <button class="vtog active" id="v-cards" onclick="setView('cards')">⊞ Cards</button>
  <button class="vtog"        id="v-table" onclick="setView('table')">☰ Table</button>
</div>

<!-- ── Card grid ─────────────────────────────────────────── -->
<div id="grid">
  <div id="loading" style="grid-column:1/-1;text-align:center;
       padding:60px;color:#8b949e;font-size:.9rem">
    ⏳ Waiting for sensor data…
  </div>
</div>

<!-- ── Table view ────────────────────────────────────────── -->
<div id="tbl-wrap">
  <table id="data-table">
    <thead>
      <tr>
        <th>NODE</th>
        <th>Ax (g)</th><th>Ay (g)</th><th>Az (g)</th>
        <th>Gx °/s</th><th>Gy °/s</th><th>Gz °/s</th>
        <th>RMS</th>
        <th>FREQ Hz</th>
        <th>INTENS %</th>
        <th>STATUS</th>
      </tr>
    </thead>
    <tbody id="tbl-body"></tbody>
  </table>
</div>

<script>
// ============================================================
// State
// ============================================================
const WSURL      = `ws://${location.host}/ws`;
let   ws;
let   packets    = 0;
let   alertCount = 0;
let   trayOpen   = false;
let   cardsBuilt = false;
let   currentView = 'cards';
let   lastNodeData = [];      // Snapshot for CSV export
let   rateWindow   = [];
const startTime    = Date.now();

// ============================================================
// View toggle
// ============================================================
function setView(v) {
    currentView = v;
    document.getElementById('grid').style.display    = v === 'cards' ? 'grid'  : 'none';
    document.getElementById('tbl-wrap').style.display = v === 'table' ? 'block' : 'none';
    document.getElementById('v-cards').classList.toggle('active', v === 'cards');
    document.getElementById('v-table').classList.toggle('active', v === 'table');
}

// ============================================================
// Build card grid (once on first data)
// ============================================================
function buildCards(n) {
    const g = document.getElementById('grid');
    g.innerHTML = '';
    for (let i = 0; i < n; i++) {
        g.innerHTML += `
        <div class="card" id="card-${i}">
          <div class="card-header">
            <div>
              <div class="card-label">Sensor Node</div>
              <div class="card-id" id="cid-${i}">Node ${i}</div>
            </div>
            <span class="badge b-ok" id="badge-${i}">NORMAL</span>
          </div>
          <div class="metrics">
            <div class="metric">
              <div class="m-label">RMS</div>
              <div class="m-value" id="rms-${i}">—</div>
            </div>
            <div class="metric">
              <div class="m-label">Dom. Freq</div>
              <div class="m-value" id="freq-${i}">—</div>
            </div>
            <div class="metric">
              <div class="m-label">Gyro X/Y/Z (°/s)</div>
              <div class="m-value" id="gyro-${i}" style="font-size:.73rem">—</div>
            </div>
            <div class="metric">
              <div class="m-label">Intensity</div>
              <div class="m-value" id="heat-pct-card-${i}">—</div>
            </div>
          </div>
          <div class="acc-row">
            <div class="m-label">AccX / AccY / AccZ (g)</div>
            <div class="m-value" id="acc-${i}" style="font-size:.76rem;margin-top:2px">—</div>
          </div>
          <div class="heat-label">
            <span>Heatmap</span>
            <span id="heat-pct-${i}">0%</span>
          </div>
          <div class="heatbar">
            <div class="heatfill" id="hbar-${i}"></div>
          </div>
        </div>`;
    }

    // Build table rows
    const tbody = document.getElementById('tbl-body');
    tbody.innerHTML = '';
    for (let i = 0; i < n; i++) {
        tbody.innerHTML += `<tr id="trow-${i}">
            <td>Node ${i}</td>
            <td id="t-ax-${i}">—</td><td id="t-ay-${i}">—</td><td id="t-az-${i}">—</td>
            <td id="t-gx-${i}">—</td><td id="t-gy-${i}">—</td><td id="t-gz-${i}">—</td>
            <td id="t-rms-${i}">—</td>
            <td id="t-freq-${i}">—</td>
            <td id="t-heat-${i}">—</td>
            <td><span class="tbl-status ts-ok" id="t-stat-${i}">NORMAL</span></td>
        </tr>`;
    }

    document.getElementById('s-nodes').textContent = n;
    cardsBuilt = true;
}

// ============================================================
// Heat colour: green → yellow → red
// ============================================================
function heatColor(v) {
    const r = Math.round(v > 0.5 ? (v - 0.5) * 2 * 185 + 63 : 63);
    const g = Math.round(v < 0.5 ? v * 2 * 122 + 185 : (1 - (v - 0.5) * 2) * 122 + 63);
    const b = 73;
    return `rgb(${r},${g},${b})`;
}

const fmt  = (v, d = 4) => (v == null ? '—' : Number(v).toFixed(d));

// ============================================================
// Update card + table row
// ============================================================
function updateNode(n) {
    const anom = !!n.anomaly;
    const pct  = (n.heat * 100).toFixed(1);

    // ── Card ─────────────────────────────────────────────────
    const card = document.getElementById(`card-${n.id}`);
    if (card) {
        card.classList.toggle('anomaly', anom);
        const bdg = document.getElementById(`badge-${n.id}`);
        bdg.textContent = anom ? '⚠ ANOMALY' : 'NORMAL';
        bdg.className   = 'badge ' + (anom ? 'b-anom' : 'b-ok');

        document.getElementById(`rms-${n.id}`).textContent  = fmt(n.rms, 5) + ' g';
        document.getElementById(`freq-${n.id}`).textContent = fmt(n.freq, 3) + ' Hz';
        document.getElementById(`acc-${n.id}`).textContent  =
            `${fmt(n.acc[0],3)} / ${fmt(n.acc[1],3)} / ${fmt(n.acc[2],3)}`;
        document.getElementById(`gyro-${n.id}`).textContent =
            `${fmt(n.gyro[0],1)} / ${fmt(n.gyro[1],1)} / ${fmt(n.gyro[2],1)}`;
        document.getElementById(`heat-pct-${n.id}`).textContent      = pct + '%';
        document.getElementById(`heat-pct-card-${n.id}`).textContent = pct + '%';
        const bar = document.getElementById(`hbar-${n.id}`);
        bar.style.width      = pct + '%';
        bar.style.background = heatColor(n.heat);
    }

    // ── Table row ─────────────────────────────────────────────
    const row = document.getElementById(`trow-${n.id}`);
    if (row) {
        row.classList.toggle('anom-row', anom);
        document.getElementById(`t-ax-${n.id}`).textContent   = fmt(n.acc[0],  4);
        document.getElementById(`t-ay-${n.id}`).textContent   = fmt(n.acc[1],  4);
        document.getElementById(`t-az-${n.id}`).textContent   = fmt(n.acc[2],  4);
        document.getElementById(`t-gx-${n.id}`).textContent   = fmt(n.gyro[0], 2);
        document.getElementById(`t-gy-${n.id}`).textContent   = fmt(n.gyro[1], 2);
        document.getElementById(`t-gz-${n.id}`).textContent   = fmt(n.gyro[2], 2);
        document.getElementById(`t-rms-${n.id}`).textContent  = fmt(n.rms,  5);
        document.getElementById(`t-freq-${n.id}`).textContent = fmt(n.freq, 3);
        document.getElementById(`t-heat-${n.id}`).textContent = pct + '%';
        const stat = document.getElementById(`t-stat-${n.id}`);
        stat.textContent = anom ? '⚠ ANOMALY' : 'NORMAL';
        stat.className   = 'tbl-status ' + (anom ? 'ts-anom' : 'ts-ok');
    }
}

// ============================================================
// Anomaly Side Tray — FIX ②
//
// addAlertToTray() is called once per event (because the
// firmware now only sends event:"alert" on newAnomaly==true).
// The tray slides in once, accumulates entries, and can be
// minimized to a badge — it never auto-dismisses or respawns.
// ============================================================
function addAlertToTray(msg) {
    // Remove empty-state placeholder
    const emptyMsg = document.getElementById('tray-empty-msg');
    if (emptyMsg) emptyMsg.remove();

    alertCount++;
    document.getElementById('tray-count').textContent  = alertCount;
    document.getElementById('badge-num').textContent   = alertCount;

    // Parse message format: "Node X — RMS=...  Freq=...  Heat=..."
    const parts   = msg.split('—');
    const nodeStr = parts[0] ? parts[0].trim() : 'Unknown Node';
    const detail  = parts[1] ? parts[1].trim() : msg;

    const entry   = document.createElement('div');
    entry.className = 'tray-entry';
    entry.innerHTML = `
        <div class="te-node">⚠ ${nodeStr}</div>
        <div class="te-detail">${detail}</div>
        <div class="te-time">${new Date().toLocaleTimeString()}</div>`;

    const body = document.getElementById('tray-body');
    body.insertBefore(entry, body.firstChild);  // newest at top

    // Open tray if not already open (only slides in once per event)
    if (!trayOpen) openTray();
}

function openTray() {
    document.getElementById('anom-tray').classList.add('open');
    document.getElementById('anom-badge').style.display = 'none';
    trayOpen = true;
}

function minimizeTray() {
    document.getElementById('anom-tray').classList.remove('open');
    // Show badge only if there are active alerts
    if (alertCount > 0) {
        document.getElementById('anom-badge').style.display = 'block';
    }
    trayOpen = false;
}

function clearAlerts() {
    alertCount = 0;
    document.getElementById('tray-count').textContent = '0';
    document.getElementById('badge-num').textContent  = '0';
    document.getElementById('anom-badge').style.display = 'none';
    document.getElementById('tray-body').innerHTML =
        '<div class="tray-empty" id="tray-empty-msg">No anomalies detected.</div>';
}

// ============================================================
// CSV Download  — FIX ③: pure Blob, zero internet required
//
// Generates CSV from the lastNodeData array that is updated
// on every WebSocket frame. No fetch(), no CDN, no server call.
// Works fully offline on the ESP32's own WiFi Access Point.
// ============================================================
function downloadCSV() {
    if (!lastNodeData || !lastNodeData.length) {
        alert('No data available yet — wait for sensor data.');
        return;
    }

    const headers = [
        'Node',
        'AccX_g', 'AccY_g', 'AccZ_g',
        'GyroX_dps', 'GyroY_dps', 'GyroZ_dps',
        'RMS_g', 'Freq_Hz',
        'Heatmap_0to1', 'Intensity_pct',
        'Anomaly',
        'Timestamp_ms'
    ];

    const rows = [headers.join(',')];

    for (const n of lastNodeData) {
        rows.push([
            n.id,
            n.acc[0].toFixed(6),  n.acc[1].toFixed(6),  n.acc[2].toFixed(6),
            n.gyro[0].toFixed(4), n.gyro[1].toFixed(4), n.gyro[2].toFixed(4),
            n.rms.toFixed(6),
            n.freq.toFixed(4),
            n.heat.toFixed(5),
            (n.heat * 100).toFixed(2),
            n.anomaly ? '1' : '0',
            n.ts
        ].join(','));
    }

    // Build file name with local timestamp
    const ts  = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const csv = rows.join('\r\n');

    // Create Blob in-browser — no network call
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url  = URL.createObjectURL(blob);

    const a       = document.createElement('a');
    a.href        = url;
    a.download    = `SHM_Data_${ts}.csv`;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    // Release object URL after download starts
    setTimeout(() => URL.revokeObjectURL(url), 3000);
}

// ============================================================
// WebSocket
// ============================================================
function connect() {
    ws = new WebSocket(WSURL);
    const lbl = document.getElementById('ws-label');

    ws.onopen = () => {
        lbl.textContent = '⬤ Live';
        lbl.className   = 'lbl-ok';
    };

    ws.onmessage = e => {
        try {
            const d = JSON.parse(e.data);

            // Welcome handshake
            if (d.event === 'connected') {
                buildCards(d.nodes);
                return;
            }

            // Anomaly alert — add to side tray (not a banner popup)
            if (d.event === 'alert') {
                addAlertToTray(d.msg);
                return;
            }

            if (!d.nodes) return;

            // Build cards on first real data frame
            if (!cardsBuilt) buildCards(d.nodes.length);

            // Update all nodes
            d.nodes.forEach(updateNode);

            // Store snapshot for CSV
            lastNodeData = d.nodes;

            // Status bar
            packets++;
            const anomCount = d.anomaly_count || 0;
            document.getElementById('s-pkt').textContent  = packets;
            document.getElementById('s-anom').innerHTML   =
                `Anomalies: <b style="color:${anomCount>0?'#f85149':'#3fb950'}">${anomCount}</b>`;

            if (d.heap)
                document.getElementById('s-heap').textContent =
                    (d.heap / 1024).toFixed(1) + ' KB';

            // Max RMS / Max Freq across nodes
            const maxRMS  = Math.max(...d.nodes.map(n => n.rms  || 0));
            const maxFreq = Math.max(...d.nodes.map(n => n.freq || 0));
            document.getElementById('s-maxrms').textContent  = maxRMS.toFixed(4)  + ' g';
            document.getElementById('s-maxfreq').textContent = maxFreq.toFixed(2) + ' Hz';

            // Packet rate
            const now = Date.now();
            rateWindow.push(now);
            rateWindow = rateWindow.filter(t => now - t < 1000);
            document.getElementById('s-rate').textContent = rateWindow.length + ' Hz';

        } catch (_) {}
    };

    ws.onclose = () => {
        document.getElementById('ws-label').textContent = '⬤ Offline';
        document.getElementById('ws-label').className   = 'lbl-err';
        setTimeout(connect, 2500);
    };

    ws.onerror = () => ws.close();
}

// ── Uptime counter ────────────────────────────────────────────
setInterval(() => {
    const s = Math.floor((Date.now() - startTime) / 1000);
    document.getElementById('uptime').textContent =
        [Math.floor(s / 3600), Math.floor(s % 3600 / 60), s % 60]
        .map(v => String(v).padStart(2, '0')).join(':');
}, 1000);

connect();
</script>
</body>
</html>
)rawhtml";

// ============================================================
// WEBSOCKET EVENT HANDLER
// ============================================================

static void onWsEvent(AsyncWebSocket       *server,
                      AsyncWebSocketClient *client,
                      AwsEventType          type,
                      void                 *arg,
                      uint8_t              *data,
                      size_t                len) {
    switch (type) {
        case WS_EVT_CONNECT:
            s_clientCount++;
            Serial.printf("[WS] Client #%u connected from %s  (total: %d)\n",
                          client->id(),
                          client->remoteIP().toString().c_str(),
                          s_clientCount);
            {
                char welcome[64];
                snprintf(welcome, sizeof(welcome),
                         "{\"event\":\"connected\",\"nodes\":%d}", NUM_SENSORS);
                client->text(welcome);
            }
            break;

        case WS_EVT_DISCONNECT:
            s_clientCount = max(0, s_clientCount - 1);
            Serial.printf("[WS] Client #%u disconnected  (total: %d)\n",
                          client->id(), s_clientCount);
            break;

        case WS_EVT_DATA: {
            AwsFrameInfo *info = (AwsFrameInfo *)arg;
            if (info->final && info->index == 0 &&
                info->len == len && info->opcode == WS_TEXT) {
                char msg[128] = {};
                memcpy(msg, data, min(len, (size_t)127));
                if (strstr(msg, "\"ping\""))
                    client->text("{\"event\":\"pong\"}");
            }
            break;
        }

        case WS_EVT_ERROR:
            Serial.printf("[WS] Error on client #%u\n", client->id());
            break;

        default: break;
    }
}

// ============================================================
// INITIALISATION
// ============================================================

void websocket_server_init() {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASSWORD, AP_CHANNEL, AP_HIDDEN, AP_MAX_CLIENTS);

    IPAddress ip = WiFi.softAPIP();
    Serial.printf("[WiFi] AP started  SSID: %-16s  IP: %s\n",
                  AP_SSID, ip.toString().c_str());
    Serial.printf("[WiFi] Dashboard  →  http://%s/\n",    ip.toString().c_str());
    Serial.printf("[WiFi] WebSocket  →  ws://%s%s\n\n",  ip.toString().c_str(), WS_PATH);

    s_ws.onEvent(onWsEvent);
    s_server.addHandler(&s_ws);

    s_server.on("/", HTTP_GET, [](AsyncWebServerRequest *req) {
        req->send_P(200, "text/html", DASHBOARD_HTML);
    });

    s_server.on("/status", HTTP_GET, [](AsyncWebServerRequest *req) {
        char buf[128];
        snprintf(buf, sizeof(buf),
                 "{\"heap\":%u,\"clients\":%d,\"uptime\":%lu}",
                 esp_get_free_heap_size(), s_clientCount, millis() / 1000);
        req->send(200, "application/json", buf);
    });

    s_server.onNotFound([](AsyncWebServerRequest *req) {
        req->send(404, "text/plain", "404 Not Found");
    });

    s_server.begin();
    Serial.println("[WS] Async HTTP server started on port 80.");
}

// ============================================================
// SEND TELEMETRY
// ============================================================

void ws_sendData(IMUData       *imuData,
                 ProcessedData *procData,
                 SemaphoreHandle_t mutex) {

    uint32_t now = millis();
    if (now - s_lastCleanup > WS_CLEANUP_INTERVAL) {
        s_ws.cleanupClients(WS_MAX_CLIENTS);
        s_lastCleanup = now;
    }

    if (s_ws.count() == 0) return;

    static IMUData       snapIMU [NUM_SENSORS];
    static ProcessedData snapProc[NUM_SENSORS];

    if (xSemaphoreTake(mutex, pdMS_TO_TICKS(8)) != pdTRUE) return;
    memcpy(snapIMU,  imuData,  sizeof(IMUData)       * NUM_SENSORS);
    memcpy(snapProc, procData, sizeof(ProcessedData) * NUM_SENSORS);
    xSemaphoreGive(mutex);

    int anomalyCount = 0;
    for (int i = 0; i < NUM_SENSORS; i++)
        if (snapProc[i].anomaly) anomalyCount++;

    static char jsonBuf[JSON_BUFFER_SIZE];
    int pos = 0;

    pos += snprintf(jsonBuf + pos, JSON_BUFFER_SIZE - pos, "{\"nodes\":[");

    for (int i = 0; i < NUM_SENSORS && pos < (JSON_BUFFER_SIZE - 300); i++) {
        const IMUData      &im = snapIMU[i];
        const ProcessedData &pd = snapProc[i];

        pos += snprintf(jsonBuf + pos, JSON_BUFFER_SIZE - pos,
            "{"
            "\"id\":%d,"
            "\"acc\":[%.5f,%.5f,%.5f],"
            "\"gyro\":[%.3f,%.3f,%.3f],"
            "\"rms\":%.6f,"
            "\"freq\":%.4f,"
            "\"heat\":%.5f,"
            "\"anomaly\":%s,"
            "\"ts\":%lu"
            "}%s",
            i,
            im.accX,  im.accY,  im.accZ,
            im.gyroX, im.gyroY, im.gyroZ,
            pd.rms,
            pd.dominantFreq,
            pd.heatmap,
            pd.anomaly ? "true" : "false",
            pd.timestamp,
            (i < NUM_SENSORS - 1) ? "," : ""
        );
    }

    pos += snprintf(jsonBuf + pos, JSON_BUFFER_SIZE - pos,
                    "],\"anomaly_count\":%d,\"heap\":%u,\"ts\":%lu}",
                    anomalyCount, esp_get_free_heap_size(), now);

    s_ws.textAll(jsonBuf);
}

// ============================================================
// UTILITIES
// ============================================================

int ws_getConnectedClients() { return s_ws.count(); }

void ws_broadcastAlert(const char *message) {
    static char alertBuf[256];
    char sanitised[200] = {};
    int j = 0;
    for (int i = 0; message[i] && j < 195; i++)
        sanitised[j++] = (message[i] == '"') ? '\'' : message[i];
    snprintf(alertBuf, sizeof(alertBuf),
             "{\"event\":\"alert\",\"msg\":\"%s\"}", sanitised);
    s_ws.textAll(alertBuf);
}

void ws_broadcastJSON(const char *json) { s_ws.textAll(json); }
