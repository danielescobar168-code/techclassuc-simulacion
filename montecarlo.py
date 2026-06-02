
"""
montecarlo.py
Ejecuta N réplicas independientes y calcula estadísticas con IC al 95%.
"""

import math
from simulacion_des import correr_una_replica


def correr_replicas(N, lam, mu, c, T_sim, T_warm=60, semilla_base=42):
    """
    Ejecuta N réplicas independientes de la simulación DES.
    Retorna diccionario con medias, desviaciones e intervalos de confianza.
    """
    Wq_medias = []
    Ws_medias = []
    n_clientes_lista = []

    for i in range(N):
        semilla = semilla_base + i
        resultado = correr_una_replica(lam, mu, c, T_sim, T_warm, semilla)
        if resultado is not None:
            Wq_medias.append(resultado["Wq_mean"])
            Ws_medias.append(resultado["Ws_mean"])
            n_clientes_lista.append(resultado["n_clientes"])

    n = len(Wq_medias)

    def estadisticas(datos):
        media = sum(datos) / n
        varianza = sum((x - media) ** 2 for x in datos) / (n - 1)
        std = math.sqrt(varianza)
        # IC 95% con t de Student aprox z=1.96 para n>=30
        margen = 1.96 * std / math.sqrt(n)
        return media, std, margen

    Wq_media, Wq_std, Wq_margen = estadisticas(Wq_medias)
    Ws_media, Ws_std, Ws_margen = estadisticas(Ws_medias)

    # Número mínimo de réplicas para error relativo <= 5%
    cv_Wq = Wq_std / Wq_media  # coeficiente de variación
    N_min = math.ceil((1.96 * cv_Wq / 0.05) ** 2)

    return {
        "N_replicas"  : n,
        "Wq_media"    : Wq_media,
        "Wq_std"      : Wq_std,
        "Wq_IC_inf"   : Wq_media - Wq_margen,
        "Wq_IC_sup"   : Wq_media + Wq_margen,
        "Ws_media"    : Ws_media,
        "Ws_std"      : Ws_std,
        "Ws_IC_inf"   : Ws_media - Ws_margen,
        "Ws_IC_sup"   : Ws_media + Ws_margen,
        "N_min"       : N_min,
        "Wq_medias"   : Wq_medias,
    }


def imprimir_montecarlo(res):
    print("\n===== SIMULACIÓN DE MONTECARLO =====")
    print(f"  Réplicas ejecutadas : {res['N_replicas']}")
    print(f"  Wq media            : {res['Wq_media']:.4f} min")
    print(f"  Wq std              : {res['Wq_std']:.4f} min")
    print(f"  IC 95% Wq           : [{res['Wq_IC_inf']:.4f}, {res['Wq_IC_sup']:.4f}]")
    print(f"  Ws media            : {res['Ws_media']:.4f} min")
    print(f"  IC 95% Ws           : [{res['Ws_IC_inf']:.4f}, {res['Ws_IC_sup']:.4f}]")
    print(f"  N mínimo réplicas   : {res['N_min']}")
    print("=====================================\n")


if __name__ == "__main__":
    res = correr_replicas(N=30, lam=10, mu=4, c=3, T_sim=480, T_warm=60)
    imprimir_montecarlo(res)