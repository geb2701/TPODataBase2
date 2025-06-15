from pydantic import BaseModel

class AgregarSkillDto(BaseModel):
    skill: str
    usuario: str
