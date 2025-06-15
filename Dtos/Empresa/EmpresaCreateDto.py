from pydantic import BaseModel

class EmpresaCreateDto(BaseModel):
    nombre: str
