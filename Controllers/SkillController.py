from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from Dtos.Skill.SkillFilterDto import SkillFilterDto 
from Dtos.Skill.SkillCreateDto import SkillCreateDto
from Dtos.Skill.Skill import Skill
from Services.SkillService import SkillService

skills_router = APIRouter(prefix="/skills", tags=["Skills"])

@skills_router.post("/", response_model=Skill)
def crear_skill_endpoint(skill: SkillCreateDto):
    try:
        return SkillService.crear(skill.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@skills_router.get("/", response_model=List[Skill])
def listar_skills_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filtros: SkillFilterDto = Depends()
):
    try:
        skills = SkillService.listar()
        for field, value in filtros.model_dump(exclude_none=True).items():
            skills = [s for s in skills if s.get(field) == value]
        return skills[skip:skip + limit]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@skills_router.get("/{skill_id}", response_model=Skill)
def obtener_skill_endpoint(skill_id: str):
    try:
        skill = SkillService.obtener_por_id(skill_id)
        if not skill:
            raise HTTPException(404, "Skill no encontrada")
        return skill
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))