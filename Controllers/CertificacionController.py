from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List

from Dtos.Certificacion.Certificacion import Certificacion
from Dtos.Certificacion.CertificacionCreateDto import CertificacionCreateDto
from Services.CertificacionService import CertificacionService
from Dtos.Certificacion.CertificacionFilterDto import CertificacionFilterDto

certificacion_router = APIRouter(prefix="/certificados", tags=["certificados"])

@certificacion_router.post("/", response_model=Certificacion)
def crear_certificacion(data: CertificacionCreateDto):
    try:
        return CertificacionService.crear(data.model_dump())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear certificación: {e}")

@certificacion_router.get("/", response_model=List[Certificacion])
def listar_certificaciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    filtros: CertificacionFilterDto = Depends()
):
    try:
        certificaciones = CertificacionService.listar()
        filtros_dict = filtros.model_dump(exclude_none=True)

        for field, value in filtros_dict.items():
            certificaciones = [c for c in certificaciones if c.get(field) == value]

        return certificaciones[skip:skip + limit]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar certificaciones: {e}")

@certificacion_router.get("/{certificacion_id}", response_model=Certificacion)
def obtener_certificacion(certificacion_id: str):
    try:
        certificacion = CertificacionService.obtener_por_id(certificacion_id)
        if not certificacion:
            raise HTTPException(status_code=404, detail="Certificación no encontrada")
        return certificacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener certificación: {e}")

