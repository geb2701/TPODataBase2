from pydantic import BaseModel

class ReferirDto(BaseModel):
    idEnviado: str
    idReceptor: str
