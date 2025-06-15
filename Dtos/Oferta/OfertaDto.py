from typing import Optional
from pydantic import BaseModel

class OfertaDto(BaseModel):
    id: Optional[str]
    empresa_id: str
    puesto: str
    categoria: str
    modalidad: str
    estado: str
    skills: str
