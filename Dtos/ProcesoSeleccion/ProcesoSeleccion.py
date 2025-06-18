from pydantic import BaseModel
from typing import List, Optional

class ProcesoSeleccion(BaseModel):
    id: Optional[str]
    oferta_id: str
    candidato_id: str
    reclutador_id: str
    estado: str
    historial: List[str]
