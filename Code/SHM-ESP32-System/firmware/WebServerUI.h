#pragma once
/*
 * ============================================================
 *  WebServerUI.h  — SHM Dashboard (v8 — Fabric of Space-Time)
 *
 *  WHY v8 DIFFERS FROM v7:
 *    v7 used MeshPhongMaterial.onBeforeCompile injection.
 *    Three.js r128 runs  #include <beginnormal_vertex>  BEFORE
 *    #include <begin_vertex>  inside main(), so variables computed
 *    in the displacement chunk did not yet exist when the normal
 *    chunk ran.  Also, uAmp=0.05 is invisible on a 22-unit plane.
 *
 *  FIX (v8):
 *    Full THREE.ShaderMaterial — complete custom GLSL.
 *    No injection, no ordering bugs, total control.
 *
 *  Visualization (Marinacci radial-ripple, 3 IMU sources):
 *    One 96×96 PlaneGeometry, flat in XZ (rotated -90° X).
 *
 *    Each IMU axis drives a separate radial ripple origin:
 *      IMU-X → origin (-5.5, -4.0)  left-front of fabric
 *      IMU-Y → origin (  0.0,  0.0) fabric centre
 *      IMU-Z → origin ( 5.5, -4.0)  right-front of fabric
 *
 *    Marinacci radial formula (per origin i):
 *      dist  = length(pos.xy - origin_i)
 *      angle = -uTime * speed_i + dist * 6.0
 *      disp  = amp_i * att * (sin(angle)
 *                           + sin(angle*2 + t*0.3)*0.35
 *                           + sin(angle*3.5+ t*0.7)*0.12)
 *      att   = 1.0 / (1.0 + dist * 0.18)   ← radial fade
 *
 *    Normals: analytical cosine derivative (exact, no finite diff).
 *
 *    Fragment heat colour (signed displacement):
 *      t = 0.5 + 0.5*(totalDisp/maxAmp)   // troughs=0, crests=1
 *      0.00 → deep blue (trough)
 *      0.25 → neon teal (below mid)
 *      0.50 → cyan/green (zero crossing)
 *      0.70 → yellow (above mid)
 *      1.00 → red (crest)
 *    + Phong diffuse+specular from world-space normals.
 *    + Neon teal crest rim glow.
 *
 *  IMU smoothing:
 *    Poll-tick LPF (α=0.10) + per-frame shader lerp (rate 0.05).
 *    Amplitude: 0.50 (idle floor) → 4.0 (full vibration).
 *
 *  Alert: caution triangle below DOWNLOAD CSV.  Dim / glow.
 *  Unchanged: polling, table, HUD, CSV, orbit+touch camera.
 *  Three.js r128 from LittleFS (/three.min.js).
 * ============================================================
 */

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SHM Monitor — 192.168.4.1</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#020810;--panel:rgba(2,8,20,0.93);--border:#0a2545;
  --accent:#00e5ff;--ok:#00e676;--warn:#ffb300;--crit:#ff3d3d;
  --teal:#00fff7;--text:#a0cce0;--dim:#2a4e62;
}
body{background:var(--bg);color:var(--text);
  font-family:'Courier New',monospace;font-size:13px;
  overflow:hidden;display:flex;flex-direction:column;height:100vh;}

/* ── Viewport ─────────────────────────────────────────────── */
#vp{position:relative;flex:0 0 60vh;width:100%;background:var(--bg);}

/* ── HUD ──────────────────────────────────────────────────── */
#hud{position:absolute;top:12px;left:12px;z-index:10;
  background:var(--panel);border:1px solid var(--border);
  border-radius:8px;padding:10px 14px;min-width:210px;
  backdrop-filter:blur(6px);}
#hud h2{font-size:.85em;letter-spacing:3px;color:var(--accent);
  margin-bottom:8px;display:flex;align-items:center;gap:8px;}
.stat{color:var(--dim);margin:3px 0;font-size:.8em;}
.stat b{color:var(--text);}
#dot{width:10px;height:10px;border-radius:50%;background:var(--crit);
  flex-shrink:0;transition:background .3s;}
#dot.live{background:var(--ok);animation:pulse 1.4s ease-in-out infinite;}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(0,230,118,.6);}
  50%{box-shadow:0 0 0 6px rgba(0,230,118,0);}}

/* ── Controls ─────────────────────────────────────────────── */
#ctrl{position:absolute;top:12px;right:12px;z-index:10;
  display:flex;flex-direction:column;align-items:flex-end;gap:8px;}
button{background:#02080f;color:var(--accent);border:1px solid var(--border);
  padding:7px 14px;border-radius:6px;cursor:pointer;
  font-family:inherit;font-size:.8em;
  transition:background .15s,transform .1s;letter-spacing:1px;}
button:hover{background:#051a30;}
button:active{transform:scale(.97);}
#btn-csv{color:var(--warn);border-color:#4a3000;background:#0a0600;}
#btn-csv:hover{background:#160d00;}

/* ── Caution triangle ─────────────────────────────────────── */
#caution-wrap{display:flex;align-items:center;justify-content:flex-end;gap:7px;}
#caution-msg{font-size:.70em;color:#ff5555;letter-spacing:1px;
  max-width:130px;text-align:right;line-height:1.3;
  opacity:0;transition:opacity .3s;}
#caution-msg.show{opacity:1;}
#caution svg{width:32px;height:32px;
  transition:filter .4s,opacity .4s;display:block;}
#caution.dim  svg{opacity:.20;filter:none;}
#caution.glow svg{opacity:1;
  filter:drop-shadow(0 0 5px #ff3d3d) drop-shadow(0 0 12px #ff1a00);
  animation:caut-flash .55s ease-in-out infinite alternate;}
@keyframes caut-flash{
  from{filter:drop-shadow(0 0 4px #ff3d3d);}
  to{filter:drop-shadow(0 0 18px #ff2200) drop-shadow(0 0 34px #ff440030);}}

/* ── Legend ───────────────────────────────────────────────── */
#legend{position:absolute;bottom:12px;left:12px;z-index:10;
  background:var(--panel);border:1px solid var(--border);
  border-radius:6px;padding:8px 12px;font-size:.72em;
  backdrop-filter:blur(4px);}
#legend .bar{width:140px;height:8px;border-radius:4px;margin:5px 0;
  background:linear-gradient(to right,#1a00ff,#00fff7,#00e676,#ffb300,#ff3d3d);}
#legend .lbl{display:flex;justify-content:space-between;color:var(--dim);}
#legend .origins{margin-top:8px;color:var(--dim);line-height:1.9;}
#legend .origins span{color:var(--teal);}

/* ── Data Panel ───────────────────────────────────────────── */
#panel{flex:1;overflow-y:auto;background:#010407;
  border-top:1px solid var(--border);}
table{width:100%;border-collapse:collapse;font-size:.78em;}
thead{position:sticky;top:0;z-index:5;}
th{background:#020b18;color:var(--accent);padding:6px 10px;
  font-weight:normal;letter-spacing:1px;
  border-bottom:1px solid var(--border);text-align:center;}
td{padding:5px 10px;text-align:center;
  border-bottom:1px solid #040e1a;color:var(--text);
  transition:background .2s;}
tr:hover td{background:#041220;}
tr.anomaly td{background:rgba(200,0,0,.10);color:#faa;}
.badge{display:inline-block;padding:2px 8px;border-radius:3px;
  font-size:.85em;font-weight:bold;letter-spacing:1px;}
.ok  {background:rgba(0,230,118,.10);color:var(--ok);  border:1px solid #003e22;}
.warn{background:rgba(255,179,0, .10);color:var(--warn);border:1px solid #4a3200;}
.crit{background:rgba(255, 61,61,.10);color:var(--crit);border:1px solid #660;
  animation:flash .5s step-start infinite;}
@keyframes flash{50%{opacity:0;}}
</style>
</head>
<body>

<!-- ══ 3-D Viewport ══════════════════════════════════════════ -->
<div id="vp">
  <div id="hud">
    <h2><span id="dot"></span>SHM MONITOR</h2>
    <div class="stat">IMUs   : <b>3 x MPU6050</b></div>
    <div class="stat">Rate   : <b id="hz-val">-- Hz</b></div>
    <div class="stat">Max RMS: <b id="max-rms">--</b></div>
    <div class="stat">Max Frq: <b id="max-frq">-- Hz</b></div>
    <div class="stat">Thresh : <b id="thresh-val">calibrating...</b></div>
    <div class="stat">IP     : <b>192.168.4.1</b></div>
  </div>

  <div id="ctrl">
    <button id="btn-orbit" onclick="toggleOrbit()">&#x21BB; AUTO-ORBIT</button>
    <button id="btn-csv" onclick="window.location='/download'">&#x2B07; DOWNLOAD CSV</button>
    <div id="caution-wrap">
      <span id="caution-msg"></span>
      <div id="caution" class="dim">
        <svg viewBox="0 0 36 32" xmlns="http://www.w3.org/2000/svg">
          <polygon points="18,2 34,30 2,30"
            fill="rgba(255,30,30,0.15)" stroke="#ff3d3d"
            stroke-width="2.2" stroke-linejoin="round"/>
          <text x="18" y="25" text-anchor="middle" font-size="14"
            font-weight="bold" fill="#ff3d3d"
            font-family="Courier New,monospace">!</text>
        </svg>
      </div>
    </div>
  </div>

  <div id="legend">
    <div style="color:var(--accent);letter-spacing:2px;margin-bottom:3px;">Space-Time Fabric</div>
    <div class="bar"></div>
    <div class="lbl">
      <span>Trough</span><span>Zero</span><span>Crest</span>
    </div>
    <div class="origins">
      &#9711; Left   &#x2192; <span>IMU X-axis</span><br>
      &#9711; Centre &#x2192; <span>IMU Y-axis</span><br>
      &#9711; Right  &#x2192; <span>IMU Z-axis</span>
    </div>
  </div>
</div>

<!-- ══ Data Table ════════════════════════════════════════════ -->
<div id="panel">
  <table>
    <thead><tr>
      <th>AXIS</th>
      <th>Ax (g)</th><th>Ay (g)</th><th>Az (g)</th>
      <th>Gx /s</th><th>Gy /s</th><th>Gz /s</th>
      <th>RMS</th><th>FREQ Hz</th><th>INTENS %</th>
      <th>STATUS</th>
    </tr></thead>
    <tbody id="tbl"></tbody>
  </table>
</div>

<script src="/three.js"></script>
<script>
// ============================================================
//  RENDERER + SCENE
// ============================================================
var vp = document.getElementById('vp');
function W(){ return vp.clientWidth; }
function H(){ return vp.clientHeight; }

var renderer = new THREE.WebGLRenderer({ antialias:true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(W(), H());
vp.appendChild(renderer.domElement);

var scene = new THREE.Scene();
scene.background = new THREE.Color(0x020810);
scene.fog = new THREE.FogExp2(0x020810, 0.007);

// Grid — subtle XZ reference plane
var grid = new THREE.GridHelper(70, 70, 0x031828, 0x010d18);
grid.position.y = -5.0;
scene.add(grid);

// Camera
var ORBIT_R = 28;
var LOOK_AT = new THREE.Vector3(0, 1.0, 0);
var camera  = new THREE.PerspectiveCamera(46, W()/H(), 0.1, 300);
camera.position.set(20, 14, 20);
camera.lookAt(LOOK_AT);

// ============================================================
//  FABRIC PLANE — custom ShaderMaterial
//  PlaneGeometry lies in XY by default; rotation.x = -PI/2
//  makes it lie flat in XZ.  Displacement is along local Z
//  which becomes world Y (up) after the rotation.
// ============================================================
var SPAN = 22.0;
var SEGS = 96;

// IMU origin positions in local-plane XY space
// After rotation: local X = world X, local Y = world -Z
var O = [
  { x: -5.5, y: -4.0 },   // IMU-X  left, toward viewer
  { x:  0.0, y:  0.0 },   // IMU-Y  centre
  { x:  5.5, y: -4.0 }    // IMU-Z  right, toward viewer
];

// ---- Complete vertex shader  --------------------------------
var VS = `
  // Per-axis uniforms
  uniform float uTime;
  uniform float uAmp0;  uniform float uSpd0;
  uniform float uAmp1;  uniform float uSpd1;
  uniform float uAmp2;  uniform float uSpd2;
  uniform float uMaxAmp;

  varying vec3  vWorldNormal;
  varying vec3  vWorldPos;
  varying float vHeat;   // signed: 0=trough, 0.5=zero, 1=crest

  // --------------- Marinacci multi-harmonic ripple ---------------
  // Returns scalar Z-displacement for one radial source.
  //   dist  = distance from source origin
  //   angle = -time*speed + dist*6.0   (Marinacci formula)
  //   disp  = amp * attenuation * 3-harmonic-sine-sum
  float ripDisp(float px, float py, float ox, float oy,
                float spd, float amp) {
    float dx   = px - ox;
    float dy   = py - oy;
    float dist = sqrt(dx*dx + dy*dy);
    float ang  = -uTime * spd + dist * 6.0;
    float att  = 1.0 / (1.0 + dist * 0.18);
    return amp * att * (
        sin(ang)
      + sin(ang * 2.0 + uTime * 0.30) * 0.35
      + sin(ang * 3.5 + uTime * 0.70) * 0.12
    );
  }

  // --------------- Analytical surface gradient  -----------------
  // dDisp/dx and dDisp/dy via chain rule on the sine harmonics.
  // Used to compute exact surface normal (no finite differences).
  void ripGrad(float px, float py, float ox, float oy,
               float spd, float amp,
               out float gx, out float gy) {
    float dx   = px - ox;
    float dy   = py - oy;
    float dist = max(sqrt(dx*dx + dy*dy), 0.001);
    float ang  = -uTime * spd + dist * 6.0;
    float att  = 1.0 / (1.0 + dist * 0.18);
    // d(ripDisp)/d(angle) * d(angle)/d(dist) * d(dist)/d(px|py)
    // d(angle)/d(dist) = 6.0
    float dda  = amp * att * 6.0 * (
        cos(ang)
      + cos(ang * 2.0 + uTime * 0.30) * 0.35 * 2.0
      + cos(ang * 3.5 + uTime * 0.70) * 0.12 * 3.5
    );
    // d(dist)/d(px) = dx/dist,  d(dist)/d(py) = dy/dist
    gx = dda * dx / dist;
    gy = dda * dy / dist;
  }

  void main() {
    float px = position.x;
    float py = position.y;

    // ---- Displacement from all 3 IMU sources ----------------
    float r0 = ripDisp(px, py, ` + O[0].x.toFixed(1) + `, ` + O[0].y.toFixed(1) + `, uSpd0, uAmp0);
    float r1 = ripDisp(px, py, ` + O[1].x.toFixed(1) + `, ` + O[1].y.toFixed(1) + `, uSpd1, uAmp1);
    float r2 = ripDisp(px, py, ` + O[2].x.toFixed(1) + `, ` + O[2].y.toFixed(1) + `, uSpd2, uAmp2);
    float totalDisp = r0 + r1 + r2;

    // ---- Exact surface normals (analytical) -----------------
    float gx0, gy0, gx1, gy1, gx2, gy2;
    ripGrad(px, py, ` + O[0].x.toFixed(1) + `, ` + O[0].y.toFixed(1) + `, uSpd0, uAmp0, gx0, gy0);
    ripGrad(px, py, ` + O[1].x.toFixed(1) + `, ` + O[1].y.toFixed(1) + `, uSpd1, uAmp1, gx1, gy1);
    ripGrad(px, py, ` + O[2].x.toFixed(1) + `, ` + O[2].y.toFixed(1) + `, uSpd2, uAmp2, gx2, gy2);

    // Local Z-up surface: normal = normalize(-dZ/dx, -dZ/dy, 1)
    vec3 localNorm = normalize(vec3(
      -(gx0 + gx1 + gx2),
      -(gy0 + gy1 + gy2),
      1.0
    ));

    // Transform normal to world space for fragment lighting
    // mat3(modelMatrix) gives the rotation/scale part
    vWorldNormal = normalize(mat3(modelMatrix) * localNorm);

    // ---- Signed heat: 0=deepest trough, 0.5=zero, 1=crest ----
    float norm = uMaxAmp > 0.001 ? totalDisp / uMaxAmp : 0.0;
    vHeat = clamp(0.5 + 0.5 * norm, 0.0, 1.0);

    // ---- Final displaced position ----------------------------
    vec3 displaced = vec3(px, py, totalDisp);
    vec4 worldPos4 = modelMatrix * vec4(displaced, 1.0);
    vWorldPos = worldPos4.xyz;
    gl_Position = projectionMatrix * viewMatrix * worldPos4;
  }
`;

// ---- Complete fragment shader  ------------------------------
var FS = `
  uniform vec3  uCamPos;     // camera position for specular

  varying vec3  vWorldNormal;
  varying vec3  vWorldPos;
  varying float vHeat;

  // 5-stop signed heat palette
  //   0.00 → deep indigo  (trough)
  //   0.25 → neon teal
  //   0.50 → cyan-green   (zero crossing — fabric at rest)
  //   0.75 → yellow
  //   1.00 → red          (crest / max energy)
  vec3 heatRamp(float t) {
    vec3 c;
    if (t < 0.25) {
      c = mix(vec3(0.10, 0.00, 0.80), vec3(0.00, 0.95, 0.92), t * 4.0);
    } else if (t < 0.50) {
      c = mix(vec3(0.00, 0.95, 0.92), vec3(0.00, 0.90, 0.40), (t - 0.25) * 4.0);
    } else if (t < 0.75) {
      c = mix(vec3(0.00, 0.90, 0.40), vec3(1.00, 0.80, 0.00), (t - 0.50) * 4.0);
    } else {
      c = mix(vec3(1.00, 0.80, 0.00), vec3(1.00, 0.03, 0.00), (t - 0.75) * 4.0);
    }
    return c;
  }

  void main() {
    vec3 N = normalize(vWorldNormal);
    vec3 V = normalize(uCamPos - vWorldPos);

    // ---- World-space lights (match scene setup) --------------
    vec3 L1 = normalize(vec3( 8.0, 20.0,  8.0));   // key  (teal)
    vec3 L2 = normalize(vec3(-10.0, 8.0, -10.0));   // fill (cyan)
    vec3 L3 = normalize(vec3( 0.0,  5.0, -14.0));   // rim  (back)

    float diff1 = max(dot(N, L1), 0.0);
    float diff2 = max(dot(N, L2), 0.0) * 0.35;
    float diff3 = max(dot(N, L3), 0.0) * 0.20;
    float ambient = 0.22;
    float lighting = ambient + diff1 * 0.60 + diff2 + diff3;

    // Phong specular from key light
    vec3  R    = reflect(-L1, N);
    float spec = pow(max(dot(R, V), 0.0), 55.0) * 0.70;

    // Neon teal specular tint  +  crest rim boost
    vec3 specCol = mix(vec3(0.5, 1.0, 1.0), vec3(1.0, 0.8, 0.8),
                       clamp(vHeat * 2.0 - 1.0, 0.0, 1.0));

    // Heat base colour
    vec3 heatCol = heatRamp(vHeat);

    // Neon teal crest glow on wave peaks
    float crestGlow = pow(clamp((vHeat - 0.75) * 4.0, 0.0, 1.0), 2.0);
    heatCol += vec3(0.0, 0.85, 1.0) * crestGlow * 0.45;

    vec3 colour = heatCol * lighting + specCol * spec;

    // Subtle rim darkening at trough depth
    float troughDark = pow(clamp((0.25 - vHeat) * 4.0, 0.0, 1.0), 2.0);
    colour = mix(colour, colour * 0.4, troughDark);

    gl_FragColor = vec4(colour, 0.90);
  }
`;

// ---- Build ShaderMaterial -----------------------------------
var fabricMat = new THREE.ShaderMaterial({
  uniforms: {
    uTime:   { value: 0.0 },
    uAmp0:   { value: 0.50 },  uSpd0: { value: 0.80 },
    uAmp1:   { value: 0.50 },  uSpd1: { value: 0.80 },
    uAmp2:   { value: 0.50 },  uSpd2: { value: 0.80 },
    uMaxAmp: { value: 1.50 },
    uCamPos: { value: new THREE.Vector3(20, 14, 20) }
  },
  vertexShader:   VS,
  fragmentShader: FS,
  transparent: true,
  side:        THREE.DoubleSide
});

var fabricGeo  = new THREE.PlaneGeometry(SPAN, SPAN, SEGS, SEGS);
var fabricMesh = new THREE.Mesh(fabricGeo, fabricMat);
fabricMesh.rotation.x = -Math.PI / 2;   // lay flat in XZ
fabricMesh.position.y = 0.0;
scene.add(fabricMesh);

// Sci-fi wireframe overlay — neon teal grid lines
var wireGeo  = new THREE.PlaneGeometry(SPAN, SPAN, 24, 24);
var wireMat  = new THREE.MeshBasicMaterial({
  color: 0x004455, wireframe: true,
  transparent: true, opacity: 0.08
});
var wireMesh = new THREE.Mesh(wireGeo, wireMat);
wireMesh.rotation.x = -Math.PI / 2;
wireMesh.position.y = 0.02;
scene.add(wireMesh);

// Small pulsing spheres at each IMU origin position
var MARKER_COLORS = [ 0x00ffcc, 0x00e5ff, 0x00ccff ];
var markers = O.map(function(o, i){
  var g  = new THREE.SphereGeometry(0.12, 12, 12);
  var m  = new THREE.MeshBasicMaterial({
    color: new THREE.Color(MARKER_COLORS[i]),
    transparent: true, opacity: 0.90
  });
  var s  = new THREE.Mesh(g, m);
  // World position: local X stays X; local Y → world -Z
  s.position.set(o.x, 0.15, o.y);
  scene.add(s);
  return { mesh: s, mat: m };
});

// ============================================================
//  SMOOTHED IMU STATE
//  Two-stage smoothing:
//    1. Poll-tick LPF (α=0.10): each /data response
//    2. Frame-rate lerp (rate 0.05): rAF loop → shader uniforms
//  This completely decouples poll rate from render rate and
//  ensures all transitions feel cloth-like and fluid.
// ============================================================
var LPF_A = 0.10;   // poll-tick low-pass filter
var AMP_L = 0.05;   // frame amplitude lerp rate
var SPD_L = 0.04;   // frame speed/freq lerp rate

var sIntensity = [0.0, 0.0, 0.0];   // LPF-smoothed intensity
var sFreq      = [1.0, 1.0, 1.0];   // LPF-smoothed freq (Hz)

// Current values fed to shader each frame
var curAmp = [0.50, 0.50, 0.50];
var curSpd = [0.80, 0.80, 0.80];

var nodeWarn     = [0.08, 0.08, 0.08];
var nodeCrit     = [0.15, 0.15, 0.15];
var baselineDone = false;

// ============================================================
//  CAUTION TRIANGLE
// ============================================================
var caut    = document.getElementById('caution');
var cautMsg = document.getElementById('caution-msg');
function setCaution(active, detail) {
  caut.className = active ? 'glow' : 'dim';
  cautMsg.textContent = active ? (detail || 'ANOMALY') : '';
  cautMsg.className   = active ? 'show' : '';
}

// ============================================================
//  DATA POLL HANDLER
// ============================================================
function updateScene(data) {
  var anyAnomaly  = false;
  var anomalyAxes = [];
  var maxRMS = 0, maxFrq = 0;
  var html = '';

  data.nodes.forEach(function(n, p) {
    if (p >= 3) return;

    // Stage-1 LPF smooth
    sIntensity[p] += LPF_A * ((n.intensity || 0.0) - sIntensity[p]);
    sFreq[p]      += LPF_A * ((n.freq      || 1.0) - sFreq[p]);

    if (n.warn !== undefined) nodeWarn[p] = n.warn;
    if (n.crit !== undefined) nodeCrit[p] = n.crit;

    var isCrit = n.rms >= nodeCrit[p];
    var isWarn = n.rms >= nodeWarn[p];
    if (isCrit) { anyAnomaly = true; anomalyAxes.push(n.axis); }

    if (n.rms  > maxRMS) maxRMS = n.rms;
    if (n.freq > maxFrq) maxFrq = n.freq;

    var badge, rowCls;
    if (isCrit)      { badge = '<span class="badge crit">CRIT</span>'; rowCls = 'anomaly'; }
    else if (isWarn) { badge = '<span class="badge warn">WARN</span>'; rowCls = ''; }
    else             { badge = '<span class="badge ok">OK</span>';     rowCls = ''; }

    html +=
      '<tr class="' + rowCls + '">' +
      '<td><b>' + n.axis + '-axis</b></td>' +
      '<td>' + n.acc[0].toFixed(3) + '</td>' +
      '<td>' + n.acc[1].toFixed(3) + '</td>' +
      '<td>' + n.acc[2].toFixed(3) + '</td>' +
      '<td>' + n.gyro[0].toFixed(2) + '</td>' +
      '<td>' + n.gyro[1].toFixed(2) + '</td>' +
      '<td>' + n.gyro[2].toFixed(2) + '</td>' +
      '<td>' + n.rms.toFixed(4) + '</td>' +
      '<td>' + n.freq.toFixed(2) + '</td>' +
      '<td>' + (n.intensity * 100).toFixed(1) + '%</td>' +
      '<td>' + badge + '</td>' +
      '</tr>';
  });

  document.getElementById('tbl').innerHTML       = html;
  document.getElementById('max-rms').textContent  = maxRMS.toFixed(4) + ' g';
  document.getElementById('max-frq').textContent  = maxFrq.toFixed(2) + ' Hz';

  var allLocked = data.nodes.every(function(n){ return n.baseline_done; });
  if (allLocked && !baselineDone) baselineDone = true;
  document.getElementById('thresh-val').textContent = baselineDone
    ? 'W:' + Math.min.apply(null, nodeWarn).toFixed(4) +
      ' C:' + Math.min.apply(null, nodeCrit).toFixed(4) + ' g'
    : 'calibrating...';

  setCaution(anyAnomaly,
    anyAnomaly ? ('Axis ' + anomalyAxes.join(',') + ' CRIT') : '');
}

// ============================================================
//  HTTP POLLING — 50 ms / 20 Hz
// ============================================================
var pollOK = false, pollCnt = 0, pollT = Date.now();
setInterval(function() {
  fetch('/data')
    .then(function(r){ return r.json(); })
    .then(function(d){
      updateScene(d);
      pollOK = true; pollCnt++;
      var now = Date.now();
      if (now - pollT >= 1000) {
        document.getElementById('hz-val').textContent = pollCnt + ' Hz';
        pollCnt = 0; pollT = now;
      }
    })
    .catch(function(){ pollOK = false; });
  document.getElementById('dot').className = pollOK ? 'live' : '';
}, 50);

// ============================================================
//  CAMERA CONTROL
// ============================================================
var autoOrbit  = true;
var orbitAngle = Math.PI * 0.25;
var dragging   = false, lastMX = 0;

function toggleOrbit() {
  autoOrbit = !autoOrbit;
  document.getElementById('btn-orbit').textContent =
    autoOrbit ? '\u21BB AUTO-ORBIT' : '\u270B MANUAL';
}

renderer.domElement.addEventListener('mousedown', function(e) {
  dragging = true; lastMX = e.clientX; autoOrbit = false;
  document.getElementById('btn-orbit').textContent = '\u270B MANUAL';
});
window.addEventListener('mouseup',   function(){ dragging = false; });
window.addEventListener('mousemove', function(e) {
  if (!dragging) return;
  orbitAngle += (e.clientX - lastMX) * 0.006; lastMX = e.clientX;
  camera.position.x = Math.sin(orbitAngle) * ORBIT_R;
  camera.position.z = Math.cos(orbitAngle) * ORBIT_R;
  camera.lookAt(LOOK_AT);
});
renderer.domElement.addEventListener('touchstart', function(e) {
  dragging = true; lastMX = e.touches[0].clientX; autoOrbit = false;
}, { passive: true });
renderer.domElement.addEventListener('touchend', function(){ dragging = false; });
renderer.domElement.addEventListener('touchmove', function(e) {
  if (!dragging) return;
  orbitAngle += (e.touches[0].clientX - lastMX) * 0.006;
  lastMX = e.touches[0].clientX;
  camera.position.x = Math.sin(orbitAngle) * ORBIT_R;
  camera.position.z = Math.cos(orbitAngle) * ORBIT_R;
  camera.lookAt(LOOK_AT);
}, { passive: true });

// ============================================================
//  ANIMATION LOOP
// ============================================================
var clock = new THREE.Clock();

(function animate() {
  requestAnimationFrame(animate);
  var t = clock.getElapsedTime();

  // Auto-orbit
  if (autoOrbit) {
    orbitAngle = t * 0.055;
    camera.position.x = Math.sin(orbitAngle) * ORBIT_R;
    camera.position.y = 13.0 + Math.sin(t * 0.10) * 1.8;
    camera.position.z = Math.cos(orbitAngle) * ORBIT_R;
    camera.lookAt(LOOK_AT);
  }

  // Stage-2: per-frame lerp toward LPF-smoothed targets
  for (var i = 0; i < 3; i++) {
    // Amplitude: idle floor 0.5, scales up to 4.0 at full vibration
    var tAmp = 0.50 + sIntensity[i] * 3.50;
    // Speed: maps IMU Hz → wave propagation speed
    //   1 Hz  → ~0.6   (slow gentle rings)
    //   50 Hz → ~3.0   (fast frantic rings)
    var tSpd = 0.40 + Math.min(sFreq[i], 50.0) * 0.052;
    curAmp[i] += AMP_L * (tAmp - curAmp[i]);
    curSpd[i] += SPD_L * (tSpd - curSpd[i]);
  }

  // Feed uniforms
  var u = fabricMat.uniforms;
  u.uTime.value   = t;
  u.uAmp0.value   = curAmp[0];  u.uSpd0.value = curSpd[0];
  u.uAmp1.value   = curAmp[1];  u.uSpd1.value = curSpd[1];
  u.uAmp2.value   = curAmp[2];  u.uSpd2.value = curSpd[2];
  // maxAmp = sum of all 3 amps → heat is relative to combined peak
  u.uMaxAmp.value = curAmp[0] + curAmp[1] + curAmp[2];
  // Keep specular camera position in sync
  u.uCamPos.value.copy(camera.position);

  // Wireframe overlay brightens with average vibration
  var avgI = (sIntensity[0] + sIntensity[1] + sIntensity[2]) / 3.0;
  wireMat.opacity = 0.06 + avgI * 0.22;

  // Origin markers pulse with their own axis intensity
  for (var j = 0; j < 3; j++) {
    var si = sIntensity[j];
    markers[j].mesh.scale.setScalar(0.7 + si * 2.0);
    markers[j].mat.opacity = Math.min(1.0, 0.40 + si * 3.5);
    markers[j].mat.color.setRGB(si * 0.25, 0.85 + si * 0.15, 1.0);
  }

  renderer.render(scene, camera);
})();

// Resize
window.addEventListener('resize', function() {
  camera.aspect = W() / H();
  camera.updateProjectionMatrix();
  renderer.setSize(W(), H());
});
</script>
</body>
</html>
)rawliteral";