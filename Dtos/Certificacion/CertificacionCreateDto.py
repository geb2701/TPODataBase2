from pydantic import BaseModel, Field
from datetime import date

class CertificacionCreateDto(BaseModel):
    curso: str
    participante: str
    puntaje: float
    aprobada: bool