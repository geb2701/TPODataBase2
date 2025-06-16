from fastapi import APIRouter, HTTPException
from typing import List

from Dtos.Certificacion.Certificacion import Certificacion
from Dtos.Certificacion.CertificacionCreateDto import CertificacionCreateDto
from Services.CertificacionService import CertificacionService


certificacion_router = APIRouter(prefix="/certificados", tags=["certificados"])

@certificacion_router.post("/", response_model=Certificacion)
def crear_curso(data: CertificacionCreateDto):
    try:
        return CertificacionService.crear(data.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@certificacion_router.get("/", response_model=List[Certificacion])
def listar_cursos():
    try:
        return CertificacionService.listar()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@certificacion_router.get("/{curso_id}", response_model=Certificacion)
def obtener_curso(curso_id: str):
    try:
        curso = CertificacionService.obtener_por_id(curso_id)
        if not curso:
            raise HTTPException(status_code=404, detail="Curso no encontrado")
        return curso
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))