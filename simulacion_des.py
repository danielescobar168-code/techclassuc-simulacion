
"""
simulacion_des.py
Simulación de eventos discretos con SimPy — modelo M/M/c.
"""


import simpy
import random
from cliente import Cliente


def proceso_atencion(env, cliente, servidor, mu, resultados):
    """Proceso SimPy: el cliente espera un servidor, es atendido y se libera."""
    cliente.t_llegada = env.now

    with servidor.request() as req:
        yield req
        cliente.t_inicio_atencion = env.now

        # Tiempo de servicio exponencial (en minutos)
        t_servicio = random.expovariate(mu / 60)
        yield env.timeout(t_servicio)

        cliente.t_fin_atencion = env.now

    resultados["Wq"].append(cliente.calcular_Wq())
    resultados["Ws"].append(cliente.calcular_Ws())


def generador_llegadas(env, lam, mu, c, servidor, resultados, T_warm):
    """Genera clientes con tasa de llegada Poisson (lam clientes/hora)."""
    id_cliente = 0
    while True:
        # Tiempo entre llegadas exponencial (en minutos)
        t_entre_llegadas = random.expovariate(lam / 60)
        yield env.timeout(t_entre_llegadas)

        id_cliente += 1
        cliente = Cliente(id_cliente)
        cliente.t_llegada = env.now

        # Solo registrar métricas después del período de calentamiento
        if env.now >= T_warm:
            env.process(proceso_atencion(env, cliente, servidor, mu, resultados))
        else:
            env.process(proceso_atencion(env, cliente, servidor, mu,
                                         {"Wq": [], "Ws": []}))


def correr_una_replica(lam, mu, c, T_sim, T_warm, semilla):
    """
    Ejecuta una réplica de la simulación DES.
    Retorna diccionario con métricas de la réplica.
    lam   : clientes/hora
    mu    : clientes/hora por servidor
    c     : número de servidores
    T_sim : duración total en minutos
    T_warm: período de calentamiento en minutos
    """
    random.seed(semilla)
    env = simpy.Environment()
    servidor = simpy.Resource(env, capacity=c)
    resultados = {"Wq": [], "Ws": []}

    env.process(generador_llegadas(env, lam, mu, c, servidor, resultados, T_warm))
    env.run(until=T_sim)

    Wq_lista = resultados["Wq"]
    Ws_lista = resultados["Ws"]

    if len(Wq_lista) == 0:
        return None

    return {
        "Wq_mean": sum(Wq_lista) / len(Wq_lista),
        "Ws_mean": sum(Ws_lista) / len(Ws_lista),
        "Wq_lista": Wq_lista,
        "n_clientes": len(Wq_lista),
    }


if __name__ == "__main__":
    resultado = correr_una_replica(lam=10, mu=4, c=3,
                                   T_sim=480, T_warm=60, semilla=42)
    print(f"Clientes atendidos : {resultado['n_clientes']}")
    print(f"Wq promedio        : {resultado['Wq_mean']:.4f} min")
    print(f"Ws promedio        : {resultado['Ws_mean']:.4f} min")