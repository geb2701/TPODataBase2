from typing import Optional, List
from pydantic import BaseModel

from Dtos.Oferta.OfertaHelper import EstadoOferta

class Oferta(BaseModel):
    id: Optional[str]
    empresa_id: str
    puesto: str
    categoria: str
    modalidad: str
    estado: EstadoOferta
    skills: List[str]

