from pydantic import BaseModel

class OfertaCreateDto(BaseModel):
    empresa_id: str
    puesto: str
    categoria: str
    modalidad: str
    estado: str
    skills: str
