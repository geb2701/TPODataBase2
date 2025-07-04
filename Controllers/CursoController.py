from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from Services import CursoService
from Dtos.Curso.CursoCreateDto import CursoCreateDto
from Dtos.Curso.Curso import Curso
from Dtos.Curso.CursoFilterDto import CursoFilterDto

curso_router = APIRouter(prefix="/cursos", tags=["Cursos"])

@curso_router.post("/", response_model=Curso)
def crear_curso(data: CursoCreateDto):
    try:
        return CursoService.crear(data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear curso: {e}")

@curso_router.get("/", response_model=List[Curso])
def listar_cursos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    filtros: CursoFilterDto = Depends()
):
    try:
        cursos = CursoService.listar()
        filtros_dict = filtros.model_dump(exclude_none=True)

        if filtros_dict:
            if "skill" in filtros_dict:
                cursos = [
                    c for c in cursos if filtros_dict["skill"] in c.get("skills", [])
                ]
            for field, value in filtros_dict.items():
                if field != "skill":
                    cursos = [c for c in cursos if c.get(field) == value]

        return cursos[skip:skip + limit]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar cursos: {e}")

@curso_router.get("/{curso_id}", response_model=Curso)
def obtener_curso(curso_id: str):
    try:
        curso = CursoService.obtener_por_id(curso_id)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        return curso
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener curso: {e}")