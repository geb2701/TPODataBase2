from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class ProcesoSeleccionCreateDto(BaseModel):
    empresa_id: str
    oferta_id: str
    candidato_id: str
    reclutador_id: str
    estado: str
