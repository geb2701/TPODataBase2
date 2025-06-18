from pydantic import BaseModel
from typing import Optional, List

class ProcesoSeleccionUpdateDto(BaseModel):
    oferta_id: Optional[str]
    candidato_id: Optional[str]
    reclutador_id: Optional[str]
    estado: Optional[str]
