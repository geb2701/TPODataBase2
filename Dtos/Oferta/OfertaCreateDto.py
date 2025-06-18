from pydantic import BaseModel
from typing import List

class OfertaCreateDto(BaseModel):
    empresa_id: str
    puesto: str
    categoria: str
    modalidad: str
    estado: str
    skills: List[str]
