from pydantic import BaseModel
from typing import List, Optional

class ProcesoSeleccionDto(BaseModel):
    id: Optional[str]
    empresa_id: str
    oferta_id: str
    candidato_id: str
    reclutador_id: str
    estado: str
    historial: List[str]
