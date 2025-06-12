from typing import List, Optional
from pydantic import BaseModel

class UsuarioCreateDto(BaseModel):
    nombre: str
    email: str
