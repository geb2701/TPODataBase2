from pydantic import BaseModel
from typing import Optional
from datetime import date

class CertificacionDto(BaseModel):
    id: Optional[str]
    curso: str
    participante: str
    puntaje: float
    aprobada: bool
    fecha_emision: date