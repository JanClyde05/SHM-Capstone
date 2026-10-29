(() => {
  "use strict";

  const API = {
    status: "/api/status",
    live: "/api/live",
    sessions: "/api/sessions",
    baseline: "/api/baseline",
    precheck: "/api/session/precheck",
    start: "/api/session/start",
    stop: "/api/session/stop"
  };
  const axes = ["x", "y", "z"];
  const trafficLevels = ["NEAR_ZERO", "MEDIUM", "HEAVY"];
  const model = { connected: false, state: "IDLE", axis: "x", live: null, status: null, baseline: null };
  let toastTimer = 0;

  const byId = (id) => document.getElementById(id);
  const finite = (value) => typeof value === "number" && Number.isFinite(value);
  const formatNumber = (value, digits = 3) => finite(value) ? value.toFixed(digits) : "—";

  async function requestJson(url, options = {}) {
    const response = await fetch(url, { cache: "no-store", ...options });
    if (!response.ok) throw new Error(`Request returned ${response.status}`);
    return response.json();
  }

  async function postJson(url, payload = {}) {
    return requestJson(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }

  function showToast(message) {
    const toast = byId("toast");
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
  }

  function setConnected(connected, status = null) {
    model.connected = connected;
    model.status = status;
    if (status?.state) model.state = status.state;
    const pill = byId("nodeStatus");
    pill.classList.toggle("is-online", connected);
    pill.classList.toggle("is-offline", !connected);
    byId("nodeStatusText").textContent = connected ? "NODE CONNECTED" : "NODE DISCONNECTED";
    byId("sessionPageState").textContent = connected ? "NODE CONNECTED" : "NODE DISCONNECTED";
    updateSessionControls();
    if (status) {
      byId("firmwareVersion").textContent = status.fw_version || "—";
      byId("footerHardwareRevision").textContent = `HARDWARE REVISION ${status.hw_rev ?? "—"}`;
      byId("acquisitionState").textContent = status.state || "AWAITING DATA";
    } else {
      byId("acquisitionState").textContent = "AWAITING DATA";
    }
  }

  function updateSessionControls() {
    byId("precheckButton").disabled = !model.connected || model.state === "RECORDING";
    byId("startSessionButton").disabled = !model.connected || model.state === "RECORDING";
    byId("stopSessionButton").disabled = !model.connected || model.state !== "RECORDING";
  }

  function renderLive(payload) {
    if (!payload || typeof payload !== "object") return;
    model.live = payload;
    model.state = payload.state || model.state;
    updateSessionControls();
    byId("acquisitionState").textContent = payload.state || "AWAITING DATA";

    const stateLabel = byId("frequencyQuality");
    const validCount = axes.filter((axis) => payload.axes?.[axis]?.valid_peak === true).length;
    stateLabel.textContent = validCount > 0 ? `${validCount} AXIS${validCount === 1 ? "" : "ES"} WITH PEAK` : "NO VALID PEAK";

    axes.forEach((axis) => {
      const entry = payload.axes?.[axis] || {};
      const freq = byId(`freq${axis.toUpperCase()}`);
      const displayFrequency = entry.valid_peak === true ? formatNumber(entry.f_d_hz) : "—";
      freq.innerHTML = `${displayFrequency}<small> Hz</small>`;
      byId(`snr${axis.toUpperCase()}`).textContent = `SNR ${formatNumber(entry.snr_db, 1)} dB`;
    });

    const rates = payload.fs_est_hz || {};
    const rateValues = [rates.imu1, rates.imu2, rates.imu3];
    rateValues.forEach((rate, index) => {
      byId(`sensorRate${index + 1}`).textContent = `${formatNumber(rate, 2)} Hz`;
      byId(`sensorDot${index + 1}`).classList.toggle("is-present", finite(rate) && rate > 0);
    });
    const validRates = rateValues.filter((value) => finite(value) && value > 0);
    byId("sampleRateSummary").textContent = validRates.length
      ? `${(validRates.reduce((sum, value) => sum + value, 0) / validRates.length).toFixed(2)} Hz AVG`
      : "— Hz";

    const baselineAxis = payload.baseline?.axes || {};
    axes.forEach((axis) => setBaselineState(axis, baselineAxis[axis]?.state));
    byId("currentSessionText").textContent = payload.session_id
      ? `ACTIVE · ${payload.session_id}`
      : model.state === "RECORDING" ? "Recording in progress." : "No session is active.";
    byId("currentTrafficLevel").textContent = trafficLevels.includes(payload.traffic_level)
      ? payload.traffic_level.replace("_", " ") : "—";
    drawSpectrum(payload.axes?.[model.axis]?.spectrum || []);
  }

  function setBaselineState(axis, state) {
    const label = byId(`baselineState${axis.toUpperCase()}`);
    const allowed = ["NO BASELINE YET", "PROVISIONAL (n<5)", "WITHIN BASELINE", "OUTSIDE BASELINE – REVIEW"];
    label.textContent = allowed.includes(state) ? state : "NO BASELINE YET";
    label.classList.toggle("is-valid", state === "WITHIN BASELINE");
    label.classList.toggle("is-review", state === "OUTSIDE BASELINE – REVIEW");
  }

  function drawSpectrum(points) {
    const canvas = byId("spectrumChart");
    const rect = canvas.getBoundingClientRect();
    if (rect.width < 1 || rect.height < 1) return;
    const ratio = Math.max(1, window.devicePixelRatio || 1);
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    const width = rect.width;
    const height = rect.height;
    const left = 42;
    const right = 10;
    const top = 12;
    const bottom = 20;
    const plotWidth = width - left - right;
    const plotHeight = height - top - bottom;

    ctx.clearRect(0, 0, width, height);
    ctx.strokeStyle = "#27272a";
    ctx.lineWidth = 1;
    ctx.fillStyle = "#71717a";
    ctx.font = "9px 'JetBrains Mono', Consolas, monospace";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    for (let i = 0; i <= 4; i += 1) {
      const y = top + (plotHeight * i) / 4;
      ctx.beginPath();
      ctx.moveTo(left, y);
      ctx.lineTo(width - right, y);
      ctx.stroke();
      ctx.fillText(i === 0 ? "MAX" : i === 4 ? "0" : "", left - 8, y);
    }
    for (let i = 0; i <= 4; i += 1) {
      const x = left + (plotWidth * i) / 4;
      ctx.beginPath();
      ctx.moveTo(x, top);
      ctx.lineTo(x, top + plotHeight);
      ctx.stroke();
    }

    const clean = Array.isArray(points)
      ? points.filter((point) => Array.isArray(point) && finite(point[0]) && finite(point[1]) && point[0] >= 0 && point[0] <= 20 && point[1] >= 0)
      : [];
    const empty = byId("chartEmpty");
    empty.classList.toggle("has-data", clean.length > 1);
    if (clean.length < 2) return;

    const maxPower = Math.max(...clean.map((point) => point[1]), Number.EPSILON);
    ctx.strokeStyle = "#60a5fa";
    ctx.lineWidth = 1.8;
    ctx.beginPath();
    clean.forEach(([frequency, power], index) => {
      const x = left + (frequency / 20) * plotWidth;
      const scaled = Math.log10(1 + 9 * (power / maxPower));
      const y = top + plotHeight * (1 - scaled);
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
  }

  async function refreshStatus() {
    try {
      const status = await requestJson(API.status);
      setConnected(true, status);
      model.state = status.state || model.state;
    } catch {
      setConnected(false);
    }
  }

  async function refreshLive() {
    try {
      renderLive(await requestJson(API.live));
    } catch {
      model.live = null;
      drawSpectrum([]);
    }
  }

  async function refreshSessions() {
    try {
      const payload = await requestJson(API.sessions);
      renderSessions(Array.isArray(payload) ? payload : payload.sessions || []);
    } catch {
      renderSessions([]);
    }
  }

  function renderSessions(sessions) {
    const list = byId("recordsList");
    list.replaceChildren();
    byId("recordCount").textContent = `${sessions.length} RECORD${sessions.length === 1 ? "" : "S"}`;
    if (!sessions.length) {
      const empty = document.createElement("p");
      empty.className = "empty-state";
      empty.textContent = model.connected ? "No saved sessions are available." : "Connect to the node to view saved sessions.";
      list.append(empty);
      return;
    }
    sessions.forEach((session) => {
      const row = document.createElement("div");
      row.className = "record-row";
      const id = document.createElement("span");
      id.className = "record-id";
      id.textContent = session.session_id || "SESSION ID UNAVAILABLE";
      const level = document.createElement("span");
      level.className = "record-level";
      level.textContent = String(session.traffic_level || "—").replaceAll("_", " ");
      const state = document.createElement("span");
      state.className = `record-state${session.valid ? " is-accepted" : ""}`;
      state.textContent = session.valid ? "ACCEPTED" : "REVIEW QC";
      const duration = document.createElement("span");
      duration.className = "record-duration";
      duration.textContent = finite(session.duration_s) ? `${Math.round(session.duration_s)} s` : "—";
      const links = document.createElement("span");
      links.className = "record-links";
      const encodedId = encodeURIComponent(String(session.session_id || ""));
      if (encodedId) {
        links.append(makeDownloadLink(`/api/sessions/${encodedId}/raw`, "RAW"));
        links.append(makeDownloadLink(`/api/sessions/${encodedId}/summary`, "SUMMARY"));
      }
      row.append(id, level, state, duration, links);
      list.append(row);
    });
  }

  function makeDownloadLink(href, label) {
    const link = document.createElement("a");
    link.href = href;
    link.textContent = label;
    link.setAttribute("download", "");
    return link;
  }

  async function refreshBaseline() {
    try {
      model.baseline = await requestJson(API.baseline);
      renderBaseline(model.baseline);
    } catch {
      model.baseline = null;
      renderBaseline(null);
    }
  }

  function renderBaseline(payload) {
    const body = byId("baselineRows");
    body.replaceChildren();
    const levels = trafficLevels;
    const all = payload?.axes || {};
    let count = 0;
    axes.forEach((axis) => {
      const axisInfo = all[axis] || {};
      setBaselineState(axis, axisInfo.state);
      levels.forEach((level) => {
        const entry = axisInfo.levels?.[level] || {};
        count += 1;
        const row = document.createElement("tr");
        const values = [
          `AXIS ${axis.toUpperCase()}`,
          level.replaceAll("_", " "),
          finite(entry.n) ? String(entry.n) : "0",
          finite(entry.mean_hz) ? `${formatNumber(entry.mean_hz)} Hz` : "—",
          finite(entry.sd_hz) ? `${formatNumber(entry.sd_hz)} Hz` : "—",
          finite(entry.cv_pct) ? `${formatNumber(entry.cv_pct, 1)}%` : "—"
        ];
        values.forEach((value) => {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.append(cell);
        });
        const stateCell = document.createElement("td");
        const state = document.createElement("span");
        state.className = `table-state${entry.state === "WITHIN BASELINE" ? " is-valid" : entry.state === "OUTSIDE BASELINE – REVIEW" ? " is-review" : ""}`;
        state.textContent = entry.state || "NO BASELINE YET";
        stateCell.append(state);
        row.append(stateCell);
        body.append(row);
      });
    });
    if (count === 0) {
      const row = document.createElement("tr");
      const cell = document.createElement("td");
      cell.colSpan = 7;
      cell.className = "empty-cell";
      cell.textContent = "NO BASELINE YET";
      row.append(cell);
      body.append(row);
    }
  }

  function showView(name) {
    document.querySelectorAll(".view").forEach((view) => {
      const active = view.id === `view-${name}`;
      view.hidden = !active;
      view.classList.toggle("is-visible", active);
    });
    document.querySelectorAll(".nav-button").forEach((button) => {
      const active = button.dataset.view === name;
      button.classList.toggle("is-active", active);
      if (active) button.setAttribute("aria-current", "page");
      else button.removeAttribute("aria-current");
    });
    if (name === "data") void refreshSessions();
    if (name === "baseline") void refreshBaseline();
    if (name === "live") requestAnimationFrame(() => drawSpectrum(model.live?.axes?.[model.axis]?.spectrum || []));
  }

  async function runPrecheck() {
    byId("sessionMessage").textContent = "Checking node status…";
    try {
      const result = await postJson(API.precheck, {});
      byId("sessionMessage").textContent = result.message || (result.passed ? "PRECHECK PASSED" : "PRECHECK NEEDS ATTENTION");
    } catch {
      byId("sessionMessage").textContent = "PRECHECK IS NOT AVAILABLE FROM THE NODE.";
    }
  }

  async function startSession(event) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!form.reportValidity()) return;
    const values = new FormData(form);
    const trafficLevel = String(values.get("traffic_level") || "");
    if (!trafficLevels.includes(trafficLevel)) return;
    const payload = {
      traffic_level: trafficLevel,
      operator: String(values.get("operator") || "").trim(),
      weather_note: String(values.get("notes") || "").trim(),
      epoch: Math.floor(Date.now() / 1000)
    };
    try {
      const result = await postJson(API.start, payload);
      byId("sessionMessage").textContent = result.message || "SESSION STARTED";
      showToast(result.session_id ? `SESSION STARTED · ${result.session_id}` : "SESSION STARTED");
      await refreshStatus();
      await refreshLive();
    } catch {
      byId("sessionMessage").textContent = "SESSION START IS NOT AVAILABLE FROM THE NODE.";
    }
  }

  async function stopSession() {
    try {
      const result = await postJson(API.stop, {});
      byId("sessionMessage").textContent = result.message || "SESSION FINALIZED";
      await refreshStatus();
      await refreshLive();
      await refreshSessions();
    } catch {
      byId("sessionMessage").textContent = "SESSION STOP IS NOT AVAILABLE FROM THE NODE.";
    }
  }

  function bindEvents() {
    document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => showView(button.dataset.view)));
    document.querySelectorAll("[data-view-link]").forEach((button) => button.addEventListener("click", () => showView(button.dataset.viewLink)));
    document.querySelectorAll(".axis-switch-button").forEach((button) => button.addEventListener("click", () => {
      model.axis = button.dataset.axis;
      document.querySelectorAll(".axis-switch-button").forEach((entry) => {
        const active = entry === button;
        entry.classList.toggle("is-active", active);
        entry.setAttribute("aria-pressed", String(active));
      });
      drawSpectrum(model.live?.axes?.[model.axis]?.spectrum || []);
    }));
    byId("precheckButton").addEventListener("click", runPrecheck);
    byId("sessionForm").addEventListener("submit", startSession);
    byId("stopSessionButton").addEventListener("click", stopSession);
    window.addEventListener("resize", () => drawSpectrum(model.live?.axes?.[model.axis]?.spectrum || []));
  }

  bindEvents();
  renderSessions([]);
  renderBaseline(null);
  setConnected(false);
  requestAnimationFrame(() => drawSpectrum([]));
  void refreshStatus();
  void refreshLive();
  window.setInterval(() => { void refreshStatus(); void refreshLive(); }, 2000);
})();
