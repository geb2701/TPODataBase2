from pydantic import BaseModel
from typing import List, Optional

class EmpresaUpdateDto(BaseModel):
    nombre: Optional[str]
