from pydantic import BaseModel
from typing import List, Optional

class Usuario(BaseModel):
    id: Optional[str]
    nombre: str
    email: str
    skills: Optional[List[str]] = []
    procesoSeleccion: Optional[List[str]]
    certificaciones: Optional[List[str]]
    mentores: Optional[List[str]]
    alumnos: Optional[List[str]]
    recomendado: Optional[List[str]] #a quien recomienda
    referido: Optional[List[str]] #quien lo recomienda
