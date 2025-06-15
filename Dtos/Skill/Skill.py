from enum import Enum
from typing import Optional
from pydantic import BaseModel, computed_field

from Dtos.Skill.SkillHelper import TipoSkill
from Dtos.Skill.SkillHelper import NivelSkill
    
class Skill(BaseModel):
    id: Optional[str]
    nombre: str
    nivel: NivelSkill
    tipo: TipoSkill

    @computed_field
    @property
    def nivel_texto(self) -> str:
        return NivelSkill(self.nivel).name