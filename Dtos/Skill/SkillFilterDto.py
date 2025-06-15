from typing import Optional
from pydantic import BaseModel

class SkillFilterDto(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None