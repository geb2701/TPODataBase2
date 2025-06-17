# Dtos/Curso/CursoFilterDto.py
from pydantic import BaseModel
from typing import Optional

class CursoFilterDto(BaseModel):
    nombre: Optional[str] = None
    empresa_id: Optional[str] = None
    skill: Optional[str] = None  # Para filtrar por skill dentro del curso
