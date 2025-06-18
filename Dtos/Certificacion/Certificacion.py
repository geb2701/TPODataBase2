from pydantic import BaseModel
from typing import Optional
from datetime import date

class Certificacion(BaseModel):
    id: Optional[str]
    curso: str
    participante: str
    puntaje: float
    aprobada: bool