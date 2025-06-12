from __future__ import annotations  # para referencias tardías
from typing import List, Optional
from pydantic import BaseModel

class UsuarioDto(BaseModel):
    id: Optional[str]
    nombre: str
    email: str
    skills: Optional[List[str]] = []
    procesoSeleccion: Optional[List[str]] = []
    certificaciones: Optional[List[str]] = []
    alumnos: Optional[List[UsuarioDto]] = []
    recomendado: Optional[List[UsuarioDto]] = []  # a quien recomienda
    referido: Optional[List[UsuarioDto]] = []     # quien lo recomienda
