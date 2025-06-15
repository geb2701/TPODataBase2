from pydantic import BaseModel
from typing import List

class Equipo(BaseModel):
    nombre: str
    integrantes: List[str] = []
    ex_integrantes: List[str] = []
