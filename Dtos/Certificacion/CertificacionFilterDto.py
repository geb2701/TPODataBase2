from typing import Optional
from pydantic import BaseModel
from datetime import date

class CertificacionFilterDto(BaseModel):
    curso: Optional[str] = None
    participante: Optional[str] = None
    aprobada: Optional[bool] = None
    fecha_emision: Optional[date] = None
