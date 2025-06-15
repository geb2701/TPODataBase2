from pydantic import BaseModel
from typing import List

class EquipoCreateDto(BaseModel):
    nombre: str
    integrantes: List[str] = []
    ex_integrantes: List[str] = []
