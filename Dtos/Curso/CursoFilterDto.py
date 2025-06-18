from pydantic import BaseModel
from typing import Optional

class CursoFilterDto(BaseModel):
    id: Optional[str] = None
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    nivel: Optional[str] = None
    modalidad: Optional[str] = None
    duracion_horas: Optional[int] = None

