from pydantic import BaseModel

class Skill(BaseModel):
    nombre: str
    descripcion: str
    nivel: str
    tipo: str