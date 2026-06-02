

"""
servidor.py
Configuración del recurso SimPy y estadísticas por servidor.
"""
import simpy


class Servidor:
    """
    Representa el conjunto de técnicos (servidores) del sistema TechClassUC.
    Encapsula el recurso SimPy y lleva estadísticas de uso.
    """

    def __init__(self, env, capacidad):
        """
        Parámetros:
            env       : simpy.Environment activo
            capacidad : número de técnicos (c)
        """
        self.env           = env
        self.capacidad     = capacidad
        self.recurso       = simpy.Resource(env, capacity=capacidad)
        self.total_clientes = 0
        self.tiempo_ocupado = 0.0
        self._t_inicio_uso  = {}

    def solicitar(self):
        """Retorna un request al recurso SimPy."""
        return self.recurso.request()

    def registrar_inicio(self, id_cliente):
        """Registra el momento en que un técnico empieza a atender."""
        self._t_inicio_uso[id_cliente] = self.env.now
        self.total_clientes += 1

    def registrar_fin(self, id_cliente):
        """Registra el momento en que termina la atención y acumula tiempo."""
        if id_cliente in self._t_inicio_uso:
            self.tiempo_ocupado += self.env.now - self._t_inicio_uso[id_cliente]
            del self._t_inicio_uso[id_cliente]

    def utilizacion(self):
        """
        Retorna la utilización real observada.
        = tiempo total ocupado / (capacidad * tiempo simulado)
        """
        t_actual = self.env.now if self.env.now > 0 else 1
        return self.tiempo_ocupado / (self.capacidad * t_actual)

    def imprimir_estadisticas(self):
        print("\n===== ESTADÍSTICAS DEL SERVIDOR =====")
        print(f"  Técnicos (capacidad) : {self.capacidad}")
        print(f"  Clientes atendidos   : {self.total_clientes}")
        print(f"  Tiempo ocupado total : {self.tiempo_ocupado:.2f} min")
        print(f"  Utilización real     : {self.utilizacion():.4f}")
        print("=====================================\n")


if __name__ == "__main__":
    # Prueba rápida
    import random
    from cliente import Cliente

    random.seed(42)
    env = simpy.Environment()
    srv = Servidor(env, capacidad=3)

    def proceso_prueba(env, srv, cliente_id):
        cliente = Cliente(cliente_id)
        cliente.t_llegada = env.now
        req = srv.solicitar()
        yield req
        srv.registrar_inicio(cliente_id)
        yield env.timeout(random.expovariate(4 / 60))
        srv.registrar_fin(cliente_id)
        srv.recurso.release(req)

    def llegadas(env, srv):
        i = 0
        while True:
            yield env.timeout(random.expovariate(10 / 60))
            i += 1
            env.process(proceso_prueba(env, srv, i))

    env.process(llegadas(env, srv))
    env.run(until=480)
    srv.imprimir_estadisticas()
