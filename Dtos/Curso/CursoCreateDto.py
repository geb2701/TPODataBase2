from pydantic import BaseModel
from typing import List
from datetime import date


class CursoCreateDto(BaseModel):
    titulo: str
    descripcion: str
    categoria: str
    nivel: str
    modalidad: str
    duracion_horas: int
    activo: bool
    skills: List[str]
