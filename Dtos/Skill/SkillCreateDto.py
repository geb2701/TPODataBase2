from enum import Enum
from pydantic import BaseModel

from Dtos.Skill.SkillHelper import TipoSkill
from Dtos.Skill.SkillHelper import NivelSkill

class SkillCreateDto(BaseModel):
    nombre: str
    nivel: NivelSkill
    tipo: TipoSkill