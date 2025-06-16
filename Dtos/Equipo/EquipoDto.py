from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel

class EquipoDto(BaseModel):
    id: Optional[str]
    nombre: str
    empresa_id: str
    integrantes: List[str] = []
    ex_integrantes: List[str] = []
