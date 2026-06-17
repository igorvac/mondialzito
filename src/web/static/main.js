/* global Chart */
'use strict';

const MAX_POINTS = 60;

// ── Chart setup ──────────────────────────────────────────────────────────────

const chart = new Chart(document.getElementById('tempChart').getContext('2d'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Temperatura (°C)',
        data: [],
        borderColor: '#f85149',
        backgroundColor: 'rgba(248,81,73,0.08)',
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2,
        fill: true,
      },
      {
        label: 'Setpoint (°C)',
        data: [],
        borderColor: '#58a6ff',
        borderDash: [6, 3],
        pointRadius: 0,
        borderWidth: 1.5,
        fill: false,
      },
    ],
  },
  options: {
    animation: false,
    responsive: true,
    maintainAspectRatio: true,
    scales: {
      x: {
        ticks: { maxTicksLimit: 6, color: '#8b949e', maxRotation: 0 },
        grid: { color: '#21262d' },
      },
      y: {
        ticks: { color: '#8b949e' },
        grid: { color: '#21262d' },
      },
    },
    plugins: {
      legend: { labels: { color: '#c9d1d9', boxWidth: 16 } },
    },
  },
});

function pushToChart(d) {
  const label = new Date(d.ts * 1000).toLocaleTimeString('pt-BR');
  chart.data.labels.push(label);
  chart.data.datasets[0].data.push(d.temp);
  chart.data.datasets[1].data.push(d.setpoint);
  if (chart.data.labels.length > MAX_POINTS) {
    chart.data.labels.shift();
    chart.data.datasets[0].data.shift();
    chart.data.datasets[1].data.shift();
  }
  chart.update('none');  // skip animation for live updates
}

// ── Display update ────────────────────────────────────────────────────────────

let _lastSetpoint = null;

function updateDisplay(d) {
  document.getElementById('currentTemp').textContent = d.temp.toFixed(1);

  const dot   = document.getElementById('ssrDot');
  const label = document.getElementById('ssrLabel');
  dot.className   = 'ssr-dot ' + (d.ssr ? 'on' : 'off');
  label.textContent = d.ssr ? 'ON' : 'OFF';

  const badge = document.getElementById('runBadge');
  badge.textContent  = d.running ? 'Controlando' : 'Parado';
  badge.style.background = d.running ? '#238636' : '#484f58';

  const btn = document.getElementById('controlBtn');
  if (d.running) {
    btn.className   = 'btn btn-lg w-100 running';
    btn.textContent = '⏹ Parar';
  } else {
    btn.className   = 'btn btn-lg w-100 stopped';
    btn.textContent = '▶ Iniciar';
  }

  if (_lastSetpoint !== d.setpoint) {
    _lastSetpoint = d.setpoint;
    document.getElementById('spSlider').value  = d.setpoint;
    document.getElementById('spInput').value   = d.setpoint;
    document.getElementById('spDisplay').textContent = d.setpoint;
  }
}

// ── SSE subscription ──────────────────────────────────────────────────────────

const evtSrc = new EventSource('/stream');
evtSrc.onmessage = (e) => {
  const d = JSON.parse(e.data);
  updateDisplay(d);
  pushToChart(d);
};

// ── Load history on page start ────────────────────────────────────────────────

fetch('/history')
  .then((r) => r.json())
  .then((items) => {
    items.forEach((d) => {
      const label = new Date(d.ts * 1000).toLocaleTimeString('pt-BR');
      chart.data.labels.push(label);
      chart.data.datasets[0].data.push(d.temp);
      chart.data.datasets[1].data.push(d.setpoint);
    });
    if (chart.data.labels.length > MAX_POINTS) {
      const excess = chart.data.labels.length - MAX_POINTS;
      chart.data.labels.splice(0, excess);
      chart.data.datasets[0].data.splice(0, excess);
      chart.data.datasets[1].data.splice(0, excess);
    }
    chart.update('none');
  })
  .catch(() => {});  // silently ignore on first load with empty history

// ── Setpoint controls ─────────────────────────────────────────────────────────

let _spTimer = null;

function postSetpoint(sp) {
  fetch('/setpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ setpoint: sp }),
  }).catch(() => {});
}

function clampSp(v) {
  return Math.min(300, Math.max(0, parseFloat(v) || 0));
}

document.getElementById('spSlider').addEventListener('input', (e) => {
  const sp = clampSp(e.target.value);
  document.getElementById('spInput').value = sp;
  document.getElementById('spDisplay').textContent = sp;
  clearTimeout(_spTimer);
  _spTimer = setTimeout(() => postSetpoint(sp), 500);
});

document.getElementById('spInput').addEventListener('change', (e) => {
  const sp = clampSp(e.target.value);
  e.target.value = sp;
  document.getElementById('spSlider').value = sp;
  document.getElementById('spDisplay').textContent = sp;
  postSetpoint(sp);
});

// ── PID form ──────────────────────────────────────────────────────────────────

document.getElementById('pidForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const payload = {
    kp: parseFloat(document.getElementById('kpIn').value),
    ki: parseFloat(document.getElementById('kiIn').value),
    kd: parseFloat(document.getElementById('kdIn').value),
  };
  fetch('/pid', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  }).then(() => {
    const ok = document.getElementById('pidOk');
    ok.style.display = 'block';
    setTimeout(() => { ok.style.display = 'none'; }, 2000);
  }).catch(() => {});
});

// ── Start / Stop ──────────────────────────────────────────────────────────────

document.getElementById('controlBtn').addEventListener('click', () => {
  const running = document.getElementById('controlBtn').classList.contains('running');
  fetch('/control', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: running ? 'stop' : 'start' }),
  }).catch(() => {});
});
