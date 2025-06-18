from typing import Optional, List
from pydantic import BaseModel

class OfertaUpdateDto(BaseModel):
    puesto: Optional[str]
    categoria: Optional[str]
    modalidad: Optional[str]
    estado: Optional[str]
    skills: Optional[List[str]]
