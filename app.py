"""
app.py
API web con Flask para ejecutar la simulación TechClassUC en Render.
"""

from flask import Flask, jsonify, request
from analitico import calcular_metricas
from montecarlo import correr_replicas
from sensibilidad import analisis_sensibilidad

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "proyecto": "TechClassUC - Simulación M/M/c",
        "endpoints": {
            "/analitico": "Métricas analíticas M/M/c",
            "/simulacion": "Simulación Montecarlo (30 réplicas)",
            "/sensibilidad": "Análisis de sensibilidad c y λ"
        }
    })

@app.route('/analitico')
def analitico():
    lam = float(request.args.get('lam', 10))
    mu  = float(request.args.get('mu', 4))
    c   = int(request.args.get('c', 3))
    try:
        m = calcular_metricas(lam, mu, c)
        return jsonify({"status": "ok", "parametros": {"lam": lam, "mu": mu, "c": c}, "metricas": m})
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
        return jsonify({"status": "ok", "parametros": {"lam": lam, "mu": mu, "c": c, "N": N}, "resultados": res})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400

@app.route('/sensibilidad')
def sensibilidad():
    try:
        tabla = analisis_sensibilidad(
            lam_valores=[6, 8, 10, 12],
            c_valores=[3, 4, 5],
            mu=4, T_sim=480, T_warm=60, N=10
        )
        return jsonify({"status": "ok", "tabla": tabla})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=False)

    