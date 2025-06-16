from __future__ import annotations  # para referencias tardías
from typing import List, Optional
from pydantic import BaseModel

from Dtos.Historial import Historial

class Usuario(BaseModel):
    id: Optional[str]
    nombre: str
    email: str
    skills: Optional[List[str]] = []
    procesoSeleccion: Optional[List[str]] = []
    certificaciones: Optional[List[str]] = []
    alumnos: Optional[List[str]] = []
    recomendado: Optional[List[str]] = []  # a quien recomienda
    referido: Optional[List[str]] = []     # quien lo recomienda
    historial: Optional[List[Historial]] = []  # historial de acciones
