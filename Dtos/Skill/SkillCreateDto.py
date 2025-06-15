from enum import Enum
from pydantic import BaseModel

from Dtos.Skill.SkillHelper import TipoSkill
from Dtos.Skill.SkillHelper import Nivelkill

class SkillCreateDto(BaseModel):
    nombre: str
    nivel: Nivelkill
    tipo: TipoSkill