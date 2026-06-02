
from flask import Flask, jsonify, request, render_template_string
from analitico import calcular_metricas
from montecarlo import correr_replicas
import json

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TechClassUC — Simulación M/M/c</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: 'Segoe UI', sans-serif; background:#0f172a; color:#e2e8f0; }

  header {
    background: linear-gradient(135deg, #1e3a5f, #2e75b6);
    padding: 24px 40px;
    display: flex; align-items: center; gap: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
  }
  header h1 { font-size: 1.8rem; color: #fff; }
  header p  { font-size: 0.9rem; color: #93c5fd; margin-top: 4px; }
  .badge {
    background: #22c55e; color: #fff;
    padding: 4px 12px; border-radius: 20px;
    font-size: 0.75rem; font-weight: bold; margin-left: auto;
  }

  .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }

  /* Parámetros */
  .params-card {
    background: #1e293b; border-radius: 16px;
    padding: 24px; margin-bottom: 28px;
    border: 1px solid #334155;
  }
  .params-card h2 { color: #93c5fd; margin-bottom: 16px; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
  .params-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; }
  .param-item label { display: block; font-size: 0.75rem; color: #94a3b8; margin-bottom: 6px; }
  .param-item input {
    width: 100%; background: #0f172a; border: 1px solid #475569;
    border-radius: 8px; padding: 10px 12px; color: #e2e8f0;
    font-size: 1rem; outline: none; transition: border 0.2s;
  }
  .param-item input:focus { border-color: #2e75b6; }
  .btn-run {
    margin-top: 20px; padding: 12px 32px;
    background: linear-gradient(135deg, #2e75b6, #1e3a5f);
    color: #fff; border: none; border-radius: 10px;
    font-size: 1rem; font-weight: bold; cursor: pointer;
    transition: opacity 0.2s;
  }
  .btn-run:hover { opacity: 0.85; }
  .btn-run:disabled { opacity: 0.5; cursor: not-allowed; }

  /* KPIs */
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }
  .kpi {
    background: #1e293b; border-radius: 14px;
    padding: 20px; border: 1px solid #334155;
    border-top: 3px solid #2e75b6;
  }
  .kpi .label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
  .kpi .value { font-size: 2rem; font-weight: bold; color: #60a5fa; margin: 8px 0 4px; }
  .kpi .sub   { font-size: 0.8rem; color: #64748b; }
  .kpi.green  { border-top-color: #22c55e; }
  .kpi.green .value { color: #4ade80; }
  .kpi.red    { border-top-color: #ef4444; }
  .kpi.red .value { color: #f87171; }
  .kpi.yellow { border-top-color: #f59e0b; }
  .kpi.yellow .value { color: #fbbf24; }

  /* Charts */
  .charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
  .chart-card {
    background: #1e293b; border-radius: 14px;
    padding: 20px; border: 1px solid #334155;
  }
  .chart-card h3 { font-size: 0.85rem; color: #93c5fd; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }

  /* Tabla */
  .table-card { background: #1e293b; border-radius: 14px; padding: 24px; border: 1px solid #334155; margin-bottom: 28px; }
  .table-card h3 { font-size: 0.85rem; color: #93c5fd; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 1px; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #0f172a; color: #93c5fd; padding: 10px 14px; text-align: center; font-size: 0.8rem; }
  td { padding: 10px 14px; text-align: center; font-size: 0.85rem; border-bottom: 1px solid #1e293b; }
  tr:nth-child(even) td { background: #162032; }
  .tag-ok   { background:#166534; color:#4ade80; padding:3px 10px; border-radius:20px; font-size:0.75rem; }
  .tag-no   { background:#7f1d1d; color:#f87171; padding:3px 10px; border-radius:20px; font-size:0.75rem; }
  .tag-warn { background:#78350f; color:#fbbf24; padding:3px 10px; border-radius:20px; font-size:0.75rem; }

  /* Recomendación */
  .recomendacion {
    background: linear-gradient(135deg, #14532d, #166534);
    border-radius: 14px; padding: 24px;
    border: 1px solid #22c55e; margin-bottom: 28px;
    display: none;
  }
  .recomendacion h3 { color: #4ade80; margin-bottom: 8px; }
  .recomendacion p  { color: #bbf7d0; line-height: 1.6; }

  .spinner { display: none; margin: 40px auto; text-align: center; color: #60a5fa; font-size: 1rem; }
  @keyframes spin { to { transform: rotate(360deg); } }
  .spin-icon { display: inline-block; width: 24px; height: 24px; border: 3px solid #334155; border-top-color: #60a5fa; border-radius: 50%; animation: spin 0.8s linear infinite; margin-right: 10px; vertical-align: middle; }
  footer { text-align: center; color: #475569; font-size: 0.75rem; padding: 24px; }
  @media(max-width:700px){ .charts-grid{ grid-template-columns:1fr; } }
</style>
</head>
<body>

<header>
  <div>
    <h1>⚙️ TechClassUC — Simulación M/M/c</h1>
    <p>Modelo de colas con SimPy · Análisis de Montecarlo · Python</p>
  </div>
  <span class="badge">● LIVE</span>
</header>

<div class="container">

  <!-- Parámetros -->
  <div class="params-card">
    <h2>⚙ Parámetros de Simulación</h2>
    <div class="params-grid">
      <div class="param-item">
        <label>λ — Tasa de llegada (cl/hora)</label>
        <input type="number" id="lam" value="10" min="1" max="50" step="1">
      </div>
      <div class="param-item">
        <label>μ — Tasa de servicio (cl/hora)</label>
        <input type="number" id="mu" value="4" min="1" max="20" step="1">
      </div>
      <div class="param-item">
        <label>c — Número de técnicos</label>
        <input type="number" id="c" value="3" min="1" max="10" step="1">
      </div>
      <div class="param-item">
        <label>N — Réplicas Montecarlo</label>
        <input type="number" id="n" value="30" min="5" max="100" step="5">
      </div>
    </div>
    <button class="btn-run" onclick="correrSimulacion()">▶ Ejecutar Simulación</button>
  </div>

  <div class="spinner" id="spinner">
    <span class="spin-icon"></span> Ejecutando simulación, por favor espere...
  </div>

  <div id="resultados" style="display:none">

    <!-- KPIs -->
    <div class="kpi-grid" id="kpis"></div>

    <!-- Recomendación -->
    <div class="recomendacion" id="recomendacion">
      <h3>✅ Recomendación Operativa</h3>
      <p id="recomendacion-texto"></p>
    </div>

    <!-- Gráficas -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>📊 Wq Analítico vs Simulado</h3>
        <canvas id="chartComparacion"></canvas>
      </div>
      <div class="chart-card">
        <h3>📈 Wq promedio vs Número de técnicos</h3>
        <canvas id="chartSensibilidad"></canvas>
      </div>
    </div>

    <!-- Tabla de sensibilidad -->
    <div class="table-card">
      <h3>🔍 Análisis de Sensibilidad — Variación de c</h3>
      <table>
        <thead>
          <tr>
            <th>Técnicos (c)</th>
            <th>ρ (utilización)</th>
            <th>Wq Analítico (min)</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody id="tabla-sensibilidad"></tbody>
      </table>
    </div>

  </div>
</div>

<footer>Corporación Universitaria Remington · Modelos de Simulación 2025 · TechClassUC</footer>

<script>
let chartComp = null;
let chartSens = null;

async function correrSimulacion() {
  const lam = document.getElementById('lam').value;
  const mu  = document.getElementById('mu').value;
  const c   = document.getElementById('c').value;
  const n   = document.getElementById('n').value;

  document.getElementById('spinner').style.display = 'block';
  document.getElementById('resultados').style.display = 'none';
  document.querySelector('.btn-run').disabled = true;

  try {
    const [resAna, resSim] = await Promise.all([
      fetch(`/analitico?lam=${lam}&mu=${mu}&c=${c}`).then(r => r.json()),
      fetch(`/simulacion?lam=${lam}&mu=${mu}&c=${c}&N=${n}`).then(r => r.json())
    ]);

    if (resAna.status === 'error') {

      document.getElementById('spinner').style.display = 'none';
      document.querySelector('.btn-run').disabled = false;
      document.getElementById('resultados').style.display = 'block';
      document.getElementById('kpis').innerHTML = `
        <div class="kpi red" style="grid-column:1/-1; text-align:center; padding:30px;">
          <div class="label">⚠ Sistema Inestable</div>
          <div class="value" style="font-size:1.2rem">${resAna.mensaje}</div>
          <div class="sub" style="margin-top:8px">Aumente el número de técnicos o reduzca la tasa de llegada λ</div>
        </div>`;
      document.getElementById('recomendacion').style.display = 'none';
      document.getElementById('tabla-sensibilidad').innerHTML = '';
      return;

    }

    const ana = resAna.metricas;
    const sim = resSim.resultados;
    const rho = ana.rho;
    const Wq_ana = ana.Wq_min;
    const Wq_sim = sim.Wq_media;
    const error  = Math.abs(Wq_sim - Wq_ana) / Wq_ana * 100;

    // KPIs
    const kpiColor = rho < 0.7 ? 'green' : rho < 0.9 ? 'yellow' : 'red';
    const wqColor  = Wq_sim <= 10 ? 'green' : 'red';
    document.getElementById('kpis').innerHTML = `
      <div class="kpi ${kpiColor}">
        <div class="label">Utilización ρ</div>
        <div class="value">${(rho*100).toFixed(1)}%</div>
        <div class="sub">λ/(c·μ) = ${rho.toFixed(4)}</div>
      </div>
      <div class="kpi">
        <div class="label">P₀ — Sistema vacío</div>
        <div class="value">${(ana.P0*100).toFixed(2)}%</div>
        <div class="sub">Prob. sin clientes</div>
      </div>
      <div class="kpi">
        <div class="label">Lq — Cola promedio</div>
        <div class="value">${ana.Lq.toFixed(2)}</div>
        <div class="sub">clientes esperando</div>
      </div>
      <div class="kpi ${wqColor}">
        <div class="label">Wq Simulado</div>
        <div class="value">${Wq_sim.toFixed(1)}<span style="font-size:1rem"> min</span></div>
        <div class="sub">IC 95%: [${sim.Wq_IC_inf.toFixed(1)}, ${sim.Wq_IC_sup.toFixed(1)}]</div>
      </div>
      <div class="kpi">
        <div class="label">Wq Analítico</div>
        <div class="value">${Wq_ana.toFixed(1)}<span style="font-size:1rem"> min</span></div>
        <div class="sub">Error: ${error.toFixed(1)}%</div>
      </div>
      <div class="kpi">
        <div class="label">W — Tiempo sistema</div>
        <div class="value">${ana.W_min.toFixed(1)}<span style="font-size:1rem"> min</span></div>
        <div class="sub">L = ${ana.L.toFixed(2)} clientes</div>
      </div>
    `;

    // Recomendación
    const rec = document.getElementById('recomendacion');
    const recTxt = document.getElementById('recomendacion-texto');
    if (Wq_sim <= 10) {
      rec.style.display = 'block';
      rec.style.background = 'linear-gradient(135deg,#14532d,#166534)';
      rec.style.borderColor = '#22c55e';
      rec.querySelector('h3').textContent = '✅ Configuración Óptima';
      recTxt.textContent = `Con c=${c} técnicos el tiempo de espera es ${Wq_sim.toFixed(2)} minutos, cumpliendo el objetivo de ≤ 10 minutos. La utilización es ${(rho*100).toFixed(1)}%, lo que indica un sistema eficiente y estable.`;
    } else {
      rec.style.display = 'block';
      rec.style.background = 'linear-gradient(135deg,#7f1d1d,#991b1b)';
      rec.style.borderColor = '#ef4444';
      rec.querySelector('h3').textContent = '⚠ Se recomienda aumentar técnicos';
      recTxt.textContent = `Con c=${c} técnicos el tiempo de espera es ${Wq_sim.toFixed(2)} minutos, superando el objetivo de ≤ 10 minutos. Se recomienda aumentar el número de técnicos para mejorar el nivel de servicio.`;
    }

    // Gráfica 1: Comparación analítico vs simulado
    const ctx1 = document.getElementById('chartComparacion').getContext('2d');
    if (chartComp) chartComp.destroy();
    chartComp = new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: ['Wq Analítico', 'Wq Simulado'],
        datasets: [{
          label: 'Tiempo de espera (min)',
          data: [Wq_ana.toFixed(2), Wq_sim.toFixed(2)],
          backgroundColor: ['#3b82f6', '#22c55e'],
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
          x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
        }
      }
    });

    // Gráfica 2: Sensibilidad c vs Wq
    const sens = await fetch(`/sensibilidad_simple?lam=${lam}&mu=${mu}`).then(r => r.json());
    const ctx2 = document.getElementById('chartSensibilidad').getContext('2d');
    if (chartSens) chartSens.destroy();
    chartSens = new Chart(ctx2, {
      type: 'line',
      data: {
        labels: sens.c_valores.map(c => `c=${c}`),
        datasets: [{
          label: 'Wq (min)',
          data: sens.wq_valores,
          borderColor: '#60a5fa',
          backgroundColor: 'rgba(96,165,250,0.1)',
          borderWidth: 2, pointRadius: 5, fill: true, tension: 0.3,
        }, {
          label: 'Umbral 10 min',
          data: sens.c_valores.map(() => 10),
          borderColor: '#ef4444', borderDash: [6,4],
          borderWidth: 2, pointRadius: 0,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: {
          y: { beginAtZero: true, ticks: { color: '#94a3b8' }, grid: { color: '#1e293b' } },
          x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
        }
      }
    });

    // Tabla de sensibilidad
    let html = '';
    sens.c_valores.forEach((cv, i) => {
      const wq = sens.wq_valores[i];
      const r  = sens.rho_valores[i];
      let tag = '';
      if (wq === null) tag = '<span class="tag-no">INESTABLE</span>';
      else if (wq <= 10) tag = '<span class="tag-ok">✓ Cumple</span>';
      else tag = '<span class="tag-warn">✗ No cumple</span>';
      html += `<tr>
        <td><b>c = ${cv}</b></td>
        <td>${r >= 1 ? '≥ 1.000' : r.toFixed(3)}</td>
        <td>${wq !== null ? wq.toFixed(2) + ' min' : '—'}</td>
        <td>${tag}</td>
      </tr>`;
    });
    document.getElementById('tabla-sensibilidad').innerHTML = html;

    document.getElementById('resultados').style.display = 'block';

  } catch(e) {
    alert('Error de conexión: ' + e.message);
  } finally {
    document.getElementById('spinner').style.display = 'none';
    document.querySelector('.btn-run').disabled = false;
  }
}

// Correr automáticamente al cargar
window.onload = () => correrSimulacion();
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/analitico')
def analitico():
    lam = float(request.args.get('lam', 10))
    mu  = float(request.args.get('mu', 4))
    c   = int(request.args.get('c', 3))
    try:
        m = calcular_metricas(lam, mu, c)
        return jsonify({"status": "ok", "metricas": m})
    except ValueError as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400

@app.route('/simulacion')
def simulacion():
    lam = float(request.args.get('lam', 10))
    mu  = float(request.args.get('mu', 4))
    c   = int(request.args.get('c', 3))
    N   = int(request.args.get('N', 30))
    try:
        res = correr_replicas(N=N, lam=lam, mu=mu, c=c, T_sim=480, T_warm=60)
        res.pop("Wq_medias", None)
        return jsonify({"status": "ok", "resultados": res})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400

@app.route('/sensibilidad_simple')
def sensibilidad_simple():
    lam = float(request.args.get('lam', 10))
    mu  = float(request.args.get('mu', 4))
    c_valores = [2, 3, 4, 5, 6]
    wq_valores = []
    rho_valores = []
    for c in c_valores:
        rho = lam / (c * mu)
        rho_valores.append(round(rho, 4))
        if rho >= 1:
            wq_valores.append(None)
        else:
            try:
                m = calcular_metricas(lam, mu, c)
                wq_valores.append(round(m['Wq_min'], 2))
            except:
                wq_valores.append(None)
    return jsonify({"c_valores": c_valores, "wq_valores": wq_valores, "rho_valores": rho_valores})

if __name__ == '__main__':
    app.run(debug=False)

