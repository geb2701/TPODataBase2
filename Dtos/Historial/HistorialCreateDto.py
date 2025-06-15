from pydantic import BaseModel
from datetime import date
from typing import Literal

class HistorialCreateDto(BaseModel):
    usuario_id: str
    entidad_id: str
    tipo: Literal["usuario", "empresa", "oferta", "proceso"]
    cambio: str
    fecha: date
