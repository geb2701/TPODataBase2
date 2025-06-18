from fastapi import APIRouter, HTTPException
from typing import List
from Services.OfertaService import OfertaService
from Dtos.Oferta.OfertaDto import OfertaDto
from Dtos.Oferta.OfertaCreateDto import OfertaCreateDto
from Dtos.Oferta.OfertaUpdateDto import OfertaUpdateDto

oferta_router = APIRouter(prefix="/Ofertas", tags=["Ofertas"])

@oferta_router.post("/", response_model=OfertaDto)
def crear_oferta(data: OfertaCreateDto):
    return OfertaService.crear(data.dict())

@oferta_router.get("/", response_model=List[OfertaDto])
def listar_ofertas():
    return OfertaService.listar()

@oferta_router.get("/{oferta_id}", response_model=OfertaDto)
def obtener_oferta(oferta_id: str):
    oferta = OfertaService.obtener_por_id(oferta_id)
    if not oferta:
        raise HTTPException(404, "Oferta no encontrada")
    return oferta

@oferta_router.patch("/{oferta_id}", response_model=OfertaDto)
def actualizar_oferta(oferta_id: str, data: OfertaUpdateDto):
    if not OfertaService.obtener_por_id(oferta_id):
        raise HTTPException(404, "Oferta no encontrada")
    return OfertaService.actualizar(oferta_id, data.dict(exclude_unset=True))

@oferta_router.delete("/{oferta_id}")
def eliminar_oferta(oferta_id: str):
    if not OfertaService.obtener_por_id(oferta_id):
        raise HTTPException(404, "Oferta no encontrada")
    OfertaService.eliminar(oferta_id)
    return {"mensaje": "Oferta eliminada"}

@oferta_router.get("/empresa/{empresa_id}", response_model=List[OfertaDto])
def listar_ofertas_por_empresa(empresa_id: str):
    ofertas = OfertaService.buscar_por_empresa(empresa_id)
    if not ofertas:
        raise HTTPException(404, "No se encontraron ofertas para esta empresa")
    return ofertas

@oferta_router.get("/activas", response_model=List[OfertaDto])
def listar_ofertas_activas():
    return OfertaService.buscar_activas()
