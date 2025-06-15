from enum import Enum, IntEnum

class TipoSkill(str, Enum):
    tecnica = "tecnica"
    blanda = "blanda"

class NivelSkill(IntEnum):
    basica = 1
    media = 2
    avanzada = 3