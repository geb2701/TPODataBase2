from typing import List, Optional
from pydantic import BaseModel

class EquipoUpdateDto(BaseModel):
    nombre: Optional[str]
    empresa_id: Optional[str]
