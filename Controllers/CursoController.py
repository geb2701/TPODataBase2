from fastapi import APIRouter, HTTPException
from typing import List
from Services import CursoService
from Dtos.Curso.CursoCreateDto import CursoCreateDto
from Dtos.Curso.Curso import Curso
from Dtos.Curso.CursoUpdateDto import CursoUpdateDto
from Dtos.Curso.CursoDeleteDto import CursoDeleteDto

curso_router = APIRouter(prefix="/cursos", tags=["Cursos"])

@curso_router.post("/", response_model=Curso)
def crear_curso(data: CursoCreateDto):
    try:
        return CursoService.crear(data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@curso_router.get("/", response_model=List[Curso])
def listar_cursos():
    try:
        return CursoService.listar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@curso_router.get("/{curso_id}", response_model=Curso)
def obtener_curso(curso_id: str):
    try:
        curso = CursoService.obtener_por_id(curso_id)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        return curso
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@curso_router.patch("/{curso_id}", response_model=Curso)
def actualizar_curso(curso_id: str, data: CursoUpdateDto):
    try:
        if not CursoService.obtener_por_id(curso_id):
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        return CursoService.actualizar(curso_id, data.dict(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@curso_router.delete("/")
def eliminar_curso(data: CursoDeleteDto):
    try:
        curso = CursoService.obtener_por_id(data.id)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        CursoService.eliminar(data.id)
        return {"mensaje": "Curso eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
