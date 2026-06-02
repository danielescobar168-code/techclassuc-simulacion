
"""
cliente.py
Clase Cliente con atributos y cálculo de métricas de tiempo.
"""

class Cliente:
    """Representa una solicitud de servicio en TechClassUC."""

    def __init__(self, id_cliente, tipo="soporte", prioridad="normal"):
        """
        Parámetros:
            id_cliente  : identificador único del cliente
            tipo        : 'soporte', 'mantenimiento' o 'reclamo'
            prioridad   : 'normal' o 'urgente'
        """
        self.id_cliente        = id_cliente
        self.tipo              = tipo
        self.prioridad         = prioridad
        self.t_llegada         = 0.0   # tiempo de llegada al sistema
        self.t_inicio_atencion = 0.0   # tiempo en que empieza a ser atendido
        self.t_fin_atencion    = 0.0   # tiempo en que termina la atención

    def calcular_Wq(self):
        """Tiempo de espera en cola (minutos)."""
        return self.t_inicio_atencion - self.t_llegada

    def calcular_Ws(self):
        """Tiempo total en el sistema (minutos)."""
        return self.t_fin_atencion - self.t_llegada

    def __repr__(self):
        return (f"Cliente(id={self.id_cliente}, tipo={self.tipo}, "
                f"prioridad={self.prioridad}, Wq={self.calcular_Wq():.2f} min)")