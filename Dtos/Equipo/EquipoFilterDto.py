from pydantic import BaseModel
from typing import Optional

class EquipoFilterDto(BaseModel):
    nombre: Optional[str] = None
    empresa_id: Optional[str] = None
