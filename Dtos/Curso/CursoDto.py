from pydantic import BaseModel
from typing import List, Optional

class CursoDto(BaseModel):
    id: Optional[str]
    titulo: str
    descripcion: str
    categoria: str
    nivel: str
    modalidad: str
    duracion_horas: int
    fecha_publicacion: str
    activo: bool
    skills: List[str]
