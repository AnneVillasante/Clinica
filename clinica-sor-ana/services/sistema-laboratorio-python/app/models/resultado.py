from dataclasses import dataclass


@dataclass
class Resultado:
    paciente_id: str
    examen_id: int
    valor: str
    fecha_muestra: str
    estado: str = 'muestra_recibida'
