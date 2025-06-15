from typing import List, Optional
from pydantic import BaseModel

class ProcesoSeleccionUpdateDto(BaseModel):
    empresa_id: Optional[str]
    oferta_id: Optional[str]
    candidato_id: Optional[str]
    reclutador_id: Optional[str]
    estado: Optional[str]
    historial: Optional[List[str]]
