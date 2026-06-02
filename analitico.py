
"""
analitico.py
Fórmulas cerradas del modelo M/M/c para calcular métricas teóricas.
"""


import math


def calcular_P0(lam, mu, c):
    """
    Calcula la probabilidad de sistema vacío P0.
    lam : tasa de llegada (clientes/hora)
    mu  : tasa de servicio por servidor (clientes/hora)
    c   : número de servidores
    """
    rho = lam / (c * mu)
    if rho >= 1:
        raise ValueError(f"Sistema inestable: rho={rho:.3f} >= 1")

    suma = sum((lam / mu) ** n / math.factorial(n) for n in range(c))
    ultimo = (lam / mu) ** c / (math.factorial(c) * (1 - rho))
    P0 = 1.0 / (suma + ultimo)
    return P0


def calcular_metricas(lam, mu, c):
    """
    Retorna diccionario con todas las métricas analíticas M/M/c.
    Unidades: lam y mu en clientes/hora → tiempos en horas.
    """
    rho = lam / (c * mu)
    if rho >= 1:
        raise ValueError(f"Sistema inestable: rho={rho:.3f} >= 1")

    P0 = calcular_P0(lam, mu, c)

    # Clientes promedio en cola
    Lq = (P0 * (lam / mu) ** c * rho) / (math.factorial(c) * (1 - rho) ** 2)

    # Tiempo promedio en cola (horas) → convertir a minutos
    Wq = Lq / lam          # horas
    Wq_min = Wq * 60       # minutos

    # Clientes promedio en sistema
    L = Lq + lam / mu

    # Tiempo promedio en sistema
    W = Wq + 1 / mu        # horas
    W_min = W * 60         # minutos

    return {
        "rho"   : rho,
        "P0"    : P0,
        "Lq"    : Lq,
        "Wq_h"  : Wq,
        "Wq_min": Wq_min,
        "L"     : L,
        "W_h"   : W,
        "W_min" : W_min,
    }


def imprimir_metricas(metricas):
    """Imprime las métricas analíticas formateadas."""
    print("\n===== MÉTRICAS ANALÍTICAS M/M/c =====")
    print(f"  Factor de utilización  ρ  : {metricas['rho']:.4f}")
    print(f"  Prob. sistema vacío   P0  : {metricas['P0']:.4f}")
    print(f"  Clientes en cola      Lq  : {metricas['Lq']:.4f}")
    print(f"  Tiempo en cola        Wq  : {metricas['Wq_min']:.4f} min")
    print(f"  Clientes en sistema   L   : {metricas['L']:.4f}")
    print(f"  Tiempo en sistema     W   : {metricas['W_min']:.4f} min")
    print("======================================\n")


if __name__ == "__main__":
    # Prueba rápida con parámetros base
    m = calcular_metricas(lam=10, mu=4, c=3)
    imprimir_metricas(m)

    