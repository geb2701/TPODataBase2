from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from Dtos.Skill import SkillFilterDto
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
@skills_router.get("/", response_model=List[Skill])
def listar_skills_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filtros: SkillFilterDto = Depends()
):
    try:
        skills = listar_skills()
        # Filtrado automático usando los campos no nulos del DTO
        for field, value in filtros.model_dump(exclude_none=True).items():
            skills = [s for s in skills if s.get(field) == value]
        return skills[skip:skip + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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