from pydantic import BaseModel

class MensajeRespuesta(BaseModel):
    message: str