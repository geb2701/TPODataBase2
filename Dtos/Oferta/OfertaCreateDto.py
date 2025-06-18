from pydantic import BaseModel
from typing import List

from Dtos.Oferta.OfertaHelper import EstadoOferta

class OfertaCreateDto(BaseModel):
    empresa_id: str
    puesto: str
    categoria: str
    modalidad: str
    estado: EstadoOferta
    skills: List[str]
