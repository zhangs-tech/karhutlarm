const POLL_MS = 2000;
const MAX_POINTS = 300;
const STALE_MS = 15000; // no reading for this long = sensor considered offline
const MAX_CHANGES = 10;

const STATUS_COLORS = { NORMAL: "#2e9e4f", WARNING: "#e6b800", DANGER: "#d62828" };

const readings = [];
const changes = [];
let lastId = 0;
let thresholds = null;

const $ = (id) => document.getElementById(id);

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: HTTP ${res.status}`);
  return res.json();
}

function ingest(rows) {
  for (const r of rows) {
    r.ts = new Date(r.ts);
    const prev = readings.at(-1);
    if (!prev || prev.status !== r.status) {
      changes.unshift({ ts: r.ts, status: r.status });
      changes.length = Math.min(changes.length, MAX_CHANGES);
    }
    readings.push(r);
    lastId = r.id;
  }
  readings.splice(0, Math.max(0, readings.length - MAX_POINTS));
}

function thresholdLine(axis, y) {
  return {
    type: "line", xref: `${axis} domain`, x0: 0, x1: 1, yref: axis.replace("x", "y"),
    y0: y, y1: y, line: { color: "red", dash: "dash" },
  };
}

function renderChart() {
  const x = readings.map((r) => r.ts);
  const line = (key, name, color, axis) => ({
    x, y: readings.map((r) => r[key]), name, type: "scatter", mode: "lines",
    line: { color }, xaxis: axis, yaxis: axis.replace("x", "y"),
  });

  const data = [
    line("gas", "Gas", "#6a4c93", "x"),
    line("temp", "Temp", "#e76f51", "x2"),
    line("humidity", "Humidity", "#1d7fb8", "x3"),
    {
      x, y: readings.map((r) => r.gas), type: "scatter", mode: "markers",
      marker: { size: 6, color: readings.map((r) => STATUS_COLORS[r.status]) },
      text: readings.map((r) => r.status), hovertemplate: "%{text}<extra></extra>",
    },
  ];

  const layout = {
    uirevision: "keep", // preserve zoom/pan across updates
    showlegend: false,
    margin: { t: 20, b: 40, l: 70, r: 20 },
    xaxis: { matches: "x3", showticklabels: false },
    xaxis2: { matches: "x3", showticklabels: false },
    xaxis3: { type: "date" },
    yaxis: { domain: [0.7, 1], title: { text: "Gas (raw ADC)" } },
    yaxis2: { domain: [0.35, 0.65], title: { text: "Temp (°C)" } },
    yaxis3: { domain: [0, 0.3], title: { text: "Humidity (%)" } },
    shapes: thresholds ? [
      thresholdLine("x", thresholds.gas),
      thresholdLine("x2", thresholds.temp_high),
      thresholdLine("x3", thresholds.humidity_low),
    ] : [],
  };

  Plotly.react("chart", data, layout, { responsive: true });
}

function renderStatus() {
  const latest = readings.at(-1);
  const stale = !latest || Date.now() - latest.ts > STALE_MS;
  const badge = $("badge");

  if (!latest) {
    badge.textContent = "NO DATA";
    badge.style.background = "gray";
    $("latest").textContent = "Waiting for data from the ESP32...";
    $("freshness").textContent = "";
    return;
  }

  badge.textContent = stale ? `OFFLINE (${latest.status})` : latest.status;
  badge.style.background = stale ? "gray" : STATUS_COLORS[latest.status];
  $("latest").textContent =
    `Gas ${latest.gas.toFixed(0)} | Temp ${latest.temp.toFixed(1)} °C | ` +
    `Humidity ${latest.humidity.toFixed(1)} %`;
  const ago = Math.round((Date.now() - latest.ts) / 1000);
  $("freshness").textContent = `Last reading ${ago}s ago`;
}

function renderChanges() {
  $("changes").innerHTML = "";
  for (const c of changes) {
    const li = document.createElement("li");
    li.textContent = `${c.ts.toLocaleTimeString()}  ${c.status}`;
    li.style.color = STATUS_COLORS[c.status];
    $("changes").append(li);
  }
  if (!changes.length) $("changes").innerHTML = "<li>None</li>";
}

function showError(err) {
  $("error").hidden = !err;
  if (err) $("error").textContent = `Cannot reach the backend: ${err.message}`;
}

async function poll() {
  try {
    const rows = await getJSON(`/api/readings?after_id=${lastId}&limit=${MAX_POINTS}`);
    showError(null);
    if (rows.length) {
      ingest(rows);
      renderChart();
      renderChanges();
    }
  } catch (err) {
    showError(err);
  }
  renderStatus();
  setTimeout(poll, POLL_MS);
}

async function init() {
  try {
    thresholds = await getJSON("/api/thresholds");
    ingest(await getJSON(`/api/readings?limit=${MAX_POINTS}`));
  } catch (err) {
    showError(err);
  }
  renderChart();
  renderChanges();
  renderStatus();
  setTimeout(poll, POLL_MS);
}

init();
