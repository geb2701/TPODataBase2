from enum import Enum

class TipoSkill(str, Enum):
    tecnica = "tecnica"
    blanda = "blanda"

class Nivelkill(str, Enum):
    basica = "basica"
    media = "media"
    avanzada = "avanzada"