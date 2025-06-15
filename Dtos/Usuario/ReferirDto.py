from pydantic import BaseModel

class ReferirDto(BaseModel):
    recomendadorId: str
    referidoId: str
