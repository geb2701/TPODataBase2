from fastapi import APIRouter, HTTPException
from typing import List

from Dtos.Skill.SkillCreateDto import SkillCreateDto
from Dtos.Skill.Skill import Skill
from Repositories.SkillRepository import (
    crear_skill,
    listar_skills,
    obtener_skill,
    actualizar_skill,
    eliminar_skill
)

skills_router = APIRouter(prefix="/skills", tags=["Skills"])

@skills_router.post("/", response_model=Skill)
def crear_skill_endpoint(skill: SkillCreateDto):
    try:
        return crear_skill(skill.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@skills_router.get("/", response_model=List[Skill])
def listar_skills_endpoint():
    return listar_skills()

@skills_router.get("/{skill_id}", response_model=Skill)
def obtener_skill_endpoint(skill_id: str):
    skill = obtener_skill(skill_id)
    if not skill:
        raise HTTPException(404, "Skill no encontrada")
    return skill

@skills_router.patch("/{skill_id}", response_model=Skill)
def actualizar_skill_endpoint(skill_id: str, skill_update: Skill):
    update_data = {k: v for k, v in skill_update.model_dump(exclude_unset=True).items() if v is not None}
    try:
        skill = actualizar_skill(skill_id, update_data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not skill:
        raise HTTPException(404, "Skill no encontrada")
    return skill

@skills_router.delete("/{skill_id}")
def eliminar_skill_endpoint(skill_id: str):
    eliminado = eliminar_skill(skill_id)
    if not eliminado:
        raise HTTPException(404, "Skill no encontrada")
    return {"message": "Skill eliminada correctamente"}