from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class CursoUpdateDto(BaseModel):
    titulo: Optional[str]
    descripcion: Optional[str]
    categoria: Optional[str]
    nivel: Optional[str]
    modalidad: Optional[str]
    duracion_horas: Optional[int]
    activo: Optional[bool]
    skills: Optional[List[str]]
