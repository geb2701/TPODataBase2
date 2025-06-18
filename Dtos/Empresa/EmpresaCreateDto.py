# EmpresaCreateDto.py
from pydantic import BaseModel
from typing import List, Optional

class EmpresaCreateDto(BaseModel):
    nombre: str
