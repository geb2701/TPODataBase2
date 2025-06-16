from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class CursoDto(BaseModel):
    id: Optional[str]
    titulo: str
    descripcion: str
    categoria: str
    nivel: str
    modalidad: str
    duracion_horas: int
    fecha_publicacion: date
    activo: bool
    skills: List[str]
