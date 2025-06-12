from typing import List, Optional
from pydantic import BaseModel

class UsuarioUpdateDto(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
