from fastapi import APIRouter, HTTPException
from typing import List
from Services.CursoService import crear, listar, obtener_por_id, actualizar, eliminar
from Dtos.Curso.CursoCreateDto import CursoCreateDto
from Dtos.Curso.CursoDto import CursoDto
from Dtos.Curso.CursoUpdateDto import CursoUpdateDto

curso_router = APIRouter(prefix="/cursos", tags=["Cursos"])

@curso_router.post("/", response_model=CursoDto)
def crear_curso(data: CursoCreateDto):
    return crear(data.dict())

@curso_router.get("/", response_model=List[CursoDto])
def listar_cursos():
    return listar()

@curso_router.get("/{curso_id}", response_model=CursoDto)
def obtener_curso(curso_id: str):
    curso = obtener_por_id(curso_id)
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@curso_router.patch("/{curso_id}", response_model=CursoDto)
def actualizar_curso(curso_id: str, data: CursoUpdateDto):
    if not obtener_por_id(curso_id):
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return actualizar(curso_id, data.dict(exclude_unset=True))

@curso_router.delete("/{curso_id}")
def eliminar_curso(curso_id: str):
    if not obtener_por_id(curso_id):
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    eliminar(curso_id)
    return {"mensaje": "Curso eliminado"}
