from fastapi import APIRouter, HTTPException
from typing import List
from Services.OfertaService import OfertaService
from Dtos.Oferta.OfertaDto import OfertaDto
from Dtos.Oferta.OfertaCreateDto import OfertaCreateDto
from Dtos.Oferta.OfertaUpdateDto import OfertaUpdateDto

oferta_router = APIRouter(prefix="/Ofertas", tags=["Ofertas"])

@oferta_router.post("/", response_model=OfertaDto)
def crear_oferta(data: OfertaCreateDto):
    try:
        return OfertaService.crear(data.dict())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@oferta_router.get("/", response_model=List[OfertaDto])
def listar_ofertas():
    try:
        return OfertaService.listar()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@oferta_router.get("/{oferta_id}", response_model=OfertaDto)
def obtener_oferta(oferta_id: str):
    try:
        oferta = OfertaService.obtener_por_id(oferta_id)
        if not oferta:
            raise HTTPException(404, "Oferta no encontrada")
        return oferta
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@oferta_router.patch("/{oferta_id}", response_model=OfertaDto)
def actualizar_oferta(oferta_id: str, data: OfertaUpdateDto):
    try:
        if not OfertaService.obtener_por_id(oferta_id):
            raise HTTPException(404, "Oferta no encontrada")
        return OfertaService.actualizar(oferta_id, data.dict(exclude_unset=True))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@oferta_router.delete("/{oferta_id}")
def eliminar_oferta(oferta_id: str):
    try:
        if not OfertaService.obtener_por_id(oferta_id):
            raise HTTPException(404, "Oferta no encontrada")
        OfertaService.eliminar(oferta_id)
        return {"mensaje": "Oferta eliminada"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@oferta_router.get("/empresa/{empresa_id}", response_model=List[OfertaDto])
def listar_ofertas_por_empresa(empresa_id: str):
    try:
        ofertas = OfertaService.buscar_por_empresa(empresa_id)
        if not ofertas:
            raise HTTPException(404, "No se encontraron ofertas para esta empresa")
        return ofertas
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@oferta_router.get("/activas", response_model=List[OfertaDto])
def listar_ofertas_activas():
    try:
        return OfertaService.buscar_activas()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))