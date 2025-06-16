from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class Empresa(BaseModel):
    id: Optional[str]
    nombre: str
    equipos: List[str] = Field(default_factory=list)
