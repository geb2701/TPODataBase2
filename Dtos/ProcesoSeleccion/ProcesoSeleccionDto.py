from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel

class ProcesoSeleccionDto(BaseModel):
    id: Optional[str]
    empresa_id: str
    oferta_id: str
    candidato_id: str
    reclutador_id: str
    estado: str
    historial: List[str] = []
