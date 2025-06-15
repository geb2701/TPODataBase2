from __future__ import annotations
from pydantic import BaseModel
from typing import Optional
from datetime import date

class HistorialDto(BaseModel):
    id: Optional[str]
    usuario_id: str
    entidad_id: str
    tipo: str
    cambio: str
    fecha: date
