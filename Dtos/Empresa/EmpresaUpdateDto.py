# EmpresaUpdateDto.py
from pydantic import BaseModel
from typing import Optional

class EmpresaUpdateDto(BaseModel):
    nombre: Optional[str]
