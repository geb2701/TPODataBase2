from pydantic import BaseModel
from typing import List

class ProcesoSeleccionCreateDto(BaseModel):
    empresa_id: str
    oferta_id: str
    candidato_id: str
    reclutador_id: str
    estado: str
    historial: List[str] = []
