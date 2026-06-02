"""
visualizacion.py
Genera las 5 gráficas requeridas con Matplotlib.
"""


import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Para Linux sin pantalla gráfica
import math
from simulacion_des import correr_una_replica
from montecarlo import correr_replicas
from sensibilidad import analisis_sensibilidad
from analitico import calcular_metricas


def grafica_evolucion_temporal(lam=10, mu=4, c=3, T_sim=480, T_warm=60):
    """Gráfica 1: Evolución temporal del número de clientes en el sistema."""
    import simpy, random

    random.seed(42)
    env = simpy.Environment()
    servidor = simpy.Resource(env, capacity=c)

    tiempos = [0]
    clientes_en_sistema = [0]
    contador = [0]

    def proceso(env, cliente_id):
        llegada = env.now
        contador[0] += 1
        clientes_en_sistema.append(contador[0])
        tiempos.append(env.now)

        with servidor.request() as req:
            yield req
            t_servicio = random.expovariate(mu / 60)
            yield env.timeout(t_servicio)

        contador[0] -= 1
        clientes_en_sistema.append(contador[0])
        tiempos.append(env.now)

    def llegadas(env):
        i = 0
        while True:
            yield env.timeout(random.expovariate(lam / 60))
            i += 1
            env.process(proceso(env, i))

    env.process(llegadas(env))
    env.run(until=T_sim)

    plt.figure(figsize=(10, 4))
    plt.step(tiempos, clientes_en_sistema, where='post', color='steelblue')
    plt.axvline(x=T_warm, color='red', linestyle='--', label='Fin calentamiento')
    plt.xlabel('Tiempo (minutos)')
    plt.ylabel('Clientes en sistema')
    plt.title('Evolución temporal del número de clientes en el sistema')
    plt.legend()
    plt.tight_layout()
    plt.savefig('grafica1_evolucion.png', dpi=150)
    plt.close()
    print("  [OK] grafica1_evolucion.png")


def grafica_histograma_wq(lam=10, mu=4, c=3, T_sim=480, T_warm=60):
    """Gráfica 2: Histograma de tiempos de espera Wq."""
    resultado = correr_una_replica(lam, mu, c, T_sim, T_warm, semilla=42)
    Wq_lista = resultado["Wq_lista"]

    plt.figure(figsize=(8, 4))
    plt.hist(Wq_lista, bins=30, color='coral', edgecolor='black', alpha=0.8)
    plt.xlabel('Wq (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Histograma de tiempos de espera en cola (Wq)')
    plt.tight_layout()
    plt.savefig('grafica2_histograma_wq.png', dpi=150)
    plt.close()
    print("  [OK] grafica2_histograma_wq.png")


def grafica_wq_vs_c(lam=10, mu=4, T_sim=480, T_warm=60, N=30):
    """Gráfica 3: Wq promedio vs número de servidores c."""
    c_valores = [2, 3, 4, 5, 6]
    wq_valores = []

    for c in c_valores:
        rho = lam / (c * mu)
        if rho >= 1:
            wq_valores.append(None)
        else:
            res = correr_replicas(N=N, lam=lam, mu=mu, c=c,
                                  T_sim=T_sim, T_warm=T_warm)
            wq_valores.append(res["Wq_media"])

    c_validos = [c for c, w in zip(c_valores, wq_valores) if w is not None]
    wq_validos = [w for w in wq_valores if w is not None]

    plt.figure(figsize=(8, 4))
    plt.plot(c_validos, wq_validos, marker='o', color='green', linewidth=2)
    plt.axhline(y=10, color='red', linestyle='--', label='Umbral 10 min')
    plt.xlabel('Número de servidores (c)')
    plt.ylabel('Wq promedio (minutos)')
    plt.title('Tiempo de espera promedio vs Número de servidores')
    plt.legend()
    plt.tight_layout()
    plt.savefig('grafica3_wq_vs_c.png', dpi=150)
    plt.close()
    print("  [OK] grafica3_wq_vs_c.png")


def grafica_rho_vs_lam(mu=4):
    """Gráfica 4: Factor de utilización ρ vs tasa de llegada λ."""
    lam_valores = list(range(4, 20))
    c_valores = [2, 3, 4, 5]

    plt.figure(figsize=(8, 4))
    for c in c_valores:
        rhos = [lam / (c * mu) for lam in lam_valores]
        plt.plot(lam_valores, rhos, marker='s', label=f'c={c}')

    plt.axhline(y=1.0, color='black', linestyle='--', label='ρ=1 (límite)')
    plt.xlabel('Tasa de llegada λ (clientes/hora)')
    plt.ylabel('Factor de utilización ρ')
    plt.title('Factor de utilización ρ vs Tasa de llegada λ')
    plt.legend()
    plt.tight_layout()
    plt.savefig('grafica4_rho_vs_lam.png', dpi=150)
    plt.close()
    print("  [OK] grafica4_rho_vs_lam.png")


def grafica_distribucion_medias(lam=10, mu=4, c=3, T_sim=480, T_warm=60, N=30):
    """Gráfica 5: Distribución de medias de Wq entre réplicas (TCL)."""
    res = correr_replicas(N=N, lam=lam, mu=mu, c=c,
                          T_sim=T_sim, T_warm=T_warm)
    Wq_medias = res["Wq_medias"]

    plt.figure(figsize=(8, 4))
    plt.hist(Wq_medias, bins=10, color='mediumpurple',
             edgecolor='black', alpha=0.8)
    plt.axvline(x=res["Wq_media"], color='red', linestyle='--',
                label=f'Media={res["Wq_media"]:.2f} min')
    plt.xlabel('Wq media por réplica (minutos)')
    plt.ylabel('Frecuencia')
    plt.title('Distribución de medias de Wq entre réplicas (TCL)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('grafica5_distribucion_medias.png', dpi=150)
    plt.close()
    print("  [OK] grafica5_distribucion_medias.png")


if __name__ == "__main__":
    print("Generando gráficas...")
    grafica_evolucion_temporal()
    grafica_histograma_wq()
    grafica_wq_vs_c()
    grafica_rho_vs_lam()
    grafica_distribucion_medias()
    print("\nTodas las gráficas generadas correctamente.")


    