
"""
main.py
Punto de entrada principal del proyecto TechClassUC.
Ejecuta todos los módulos y genera el reporte final.
"""
from analitico import calcular_metricas, imprimir_metricas
from montecarlo import correr_replicas, imprimir_montecarlo
from sensibilidad import analisis_sensibilidad, imprimir_tabla
from visualizacion import (grafica_evolucion_temporal, grafica_histograma_wq,
                            grafica_wq_vs_c, grafica_rho_vs_lam,
                            grafica_distribucion_medias)

# ── Parámetros base ──────────────────────────────────────────
LAM    = 10    # clientes/hora
MU     = 4     # clientes/hora por técnico
C      = 3     # número de técnicos
T_SIM  = 480   # minutos (8 horas)
T_WARM = 60    # minutos de calentamiento
N      = 30    # réplicas Montecarlo

def validar_estabilidad(lam, mu, c):
    rho = lam / (c * mu)
    if rho >= 1:
        print(f"\n ERROR: Sistema inestable (ρ={rho:.3f} >= 1). "
              f"Aumente c o reduzca λ.")
        return False
    return True

def comparar_analitico_simulado(met_analitico, res_montecarlo):
    """Tabla comparativa con error relativo %."""
    Wq_sim = res_montecarlo["Wq_media"]
    Wq_ana = met_analitico["Wq_min"]
    Ws_sim = res_montecarlo["Ws_media"]
    Ws_ana = met_analitico["W_min"]

    err_Wq = abs(Wq_sim - Wq_ana) / Wq_ana * 100
    err_Ws = abs(Ws_sim - Ws_ana) / Ws_ana * 100

    print("\n===== VALIDACIÓN ANALÍTICO vs SIMULADO =====")
    print(f"{'Métrica':<10} {'Analítico':>12} {'Simulado':>12} {'Error %':>10}")
    print("-" * 48)
    print(f"{'Wq (min)':<10} {Wq_ana:>12.4f} {Wq_sim:>12.4f} {err_Wq:>9.2f}%")
    print(f"{'Ws (min)':<10} {Ws_ana:>12.4f} {Ws_sim:>12.4f} {err_Ws:>9.2f}%")
    print("=" * 48)

def recomendacion(lam, mu):
    """Encuentra el c mínimo tal que Wq < 10 min."""
    print("\n===== RECOMENDACIÓN OPERATIVA =====")
    for c in range(2, 10):
        rho = lam / (c * mu)
        if rho >= 1:
            continue
        res = correr_replicas(N=15, lam=lam, mu=mu, c=c,
                              T_sim=480, T_warm=60)
        print(f"  c={c} → Wq={res['Wq_media']:.2f} min, ρ={rho:.3f}")
        if res["Wq_media"] <= 10:
            print(f"\n  RECOMENDACIÓN: Asignar {c} técnicos.")
            print(f"  Wq={res['Wq_media']:.2f} min ≤ 10 min ✓")
            break
    print("=" * 36)

def main():
    print("=" * 50)
    print("  SIMULACIÓN TECHCLASSUC — M/M/c")
    print("=" * 50)
    print(f"  λ={LAM} cl/h | μ={MU} cl/h | c={C} | "
          f"T={T_SIM} min | N={N} réplicas")

    if not validar_estabilidad(LAM, MU, C):
        return

    # 1. Métricas analíticas
    met = calcular_metricas(LAM, MU, C)
    imprimir_metricas(met)

    # 2. Montecarlo
    print("Ejecutando Montecarlo...")
    res = correr_replicas(N, LAM, MU, C, T_SIM, T_WARM)
    imprimir_montecarlo(res)

    # 3. Validación
    comparar_analitico_simulado(met, res)

    # 4. Sensibilidad
    print("\nEjecutando análisis de sensibilidad...")
    tabla = analisis_sensibilidad([6, 8, 10, 12], [2, 3, 4, 5], MU, T_SIM, T_WARM, N=15)
    imprimir_tabla(tabla)

    # 5. Recomendación
    recomendacion(LAM, MU)

    # 6. Gráficas
    print("\nGenerando gráficas...")
    grafica_evolucion_temporal()
    grafica_histograma_wq()
    grafica_wq_vs_c()
    grafica_rho_vs_lam()
    grafica_distribucion_medias()

    print("\n Proyecto completado. Revisa las gráficas PNG generadas.")

if __name__ == "__main__":
    main()