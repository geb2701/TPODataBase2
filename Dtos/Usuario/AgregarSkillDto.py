from pydantic import BaseModel

class AgregarSkillDto(BaseModel):
    skillId: str
    usuarioId: str
