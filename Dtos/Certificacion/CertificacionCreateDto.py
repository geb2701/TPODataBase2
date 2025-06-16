from pydantic import BaseModel, Field
from datetime import date

class CertificacionCreateDto(BaseModel):
    curso: str
    participante: str
    puntaje: float
    aprobada: bool
    fecha_emision: date = Field(default_factory=date.today)