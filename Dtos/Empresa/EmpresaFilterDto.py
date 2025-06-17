from pydantic import BaseModel
from typing import Optional

class EmpresaFilterDto(BaseModel):
    nombre: Optional[str] = None
