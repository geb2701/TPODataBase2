from typing import Optional
from pydantic import BaseModel

class UsuarioFilterDto(BaseModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    # Agrega más campos según tus necesidades