from typing import Optional, List
from pydantic import BaseModel

class OfertaUpdateDto(BaseModel):
    empresa_id: Optional[str]
    puesto: Optional[str]
    categoria: Optional[str]
    modalidad: Optional[str]
    estado: Optional[str]
    skills: Optional[List[str]]
