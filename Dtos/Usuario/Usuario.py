from __future__ import annotations  # para referencias tardías
from typing import List, Optional
from pydantic import BaseModel

class Usuario(BaseModel):
    id: Optional[str]
    nombre: str
    email: str
    skills: Optional[List[str]] = []
    procesoSeleccion: Optional[List[str]] = []
    certificaciones: Optional[List[str]] = []
    alumnos: Optional[List[Usuario]] = []
    recomendado: Optional[List[Usuario]] = []  # a quien recomienda
    referido: Optional[List[Usuario]] = []     # quien lo recomienda
