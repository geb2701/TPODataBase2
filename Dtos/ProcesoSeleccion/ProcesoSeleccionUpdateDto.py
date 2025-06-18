from pydantic import BaseModel
from typing import Optional, List

class ProcesoSeleccionUpdateDto(BaseModel):
    empresa_id: Optional[str]
    oferta_id: Optional[str]
    candidato_id: Optional[str]
    reclutador_id: Optional[str]
    estado: Optional[str]
    historial: Optional[List[str]]
