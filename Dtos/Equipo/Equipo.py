from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel

from Dtos.Historial import Historial

class Equipo(BaseModel):
    id: Optional[str]
    nombre: str
    empresa_id: str
    integrantes: List[str] = []
    ex_integrantes: List[str] = []
    historial: Optional[List[Historial]] = [] 