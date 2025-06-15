from pydantic import BaseModel
from typing import List, Optional

class EquipoUpdateDto(BaseModel):
    nombre: Optional[str]
    integrantes: Optional[List[str]]
    ex_integrantes: Optional[List[str]]
