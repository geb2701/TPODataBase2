from fastapi import APIRouter, HTTPException
from typing import List
from Services import CertificacionService
from Dtos.Certificacion.CertificacionDto import CertificacionDto
from Dtos.Certificacion.CertificacionCreateDto import CertificacionCreateDto

certificacion_router = APIRouter(prefix="/certificaciones", tags=["Certificaciones"])

@certificacion_router.post("/", response_model=CertificacionDto)
def crear_certificacion(data: CertificacionCreateDto):
    try:
        return CertificacionService.crear_certificacion_y_asignar_skills(data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@certificacion_router.get("/", response_model=List[CertificacionDto])
def listar_certificaciones():
    try:
        return CertificacionService.listar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))