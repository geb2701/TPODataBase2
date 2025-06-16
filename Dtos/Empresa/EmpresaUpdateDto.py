# EmpresaUpdateDto.py
from pydantic import BaseModel
from typing import List, Optional

class EmpresaUpdateDto(BaseModel):
    nombre: Optional[str]
    equipos: Optional[List[str]] = None
