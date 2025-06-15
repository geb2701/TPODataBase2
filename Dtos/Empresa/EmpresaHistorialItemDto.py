from pydantic import BaseModel
from datetime import date

class EmpresaHistorialItemDto(BaseModel):
    cambio: str
    fecha: date
