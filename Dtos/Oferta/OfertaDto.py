from typing import Optional, List
from pydantic import BaseModel

class OfertaDto(BaseModel):
    id: Optional[str]
    empresa_id: str
    puesto: str
    categoria: str
    modalidad: str
    estado: str
    skills: List[str]

