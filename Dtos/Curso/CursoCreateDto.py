from pydantic import BaseModel
from typing import List

class CursoCreateDto(BaseModel):
    titulo: str
    descripcion: str
    categoria: str
    nivel: str
    modalidad: str
    duracion_horas: int
    fecha_publicacion: str  # formato ISO
    activo: bool
    skills: List[str]
