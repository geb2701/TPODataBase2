from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional

class Empresa(BaseModel):
    id: Optional[str]
    nombre: str
