from fastapi import APIRouter, HTTPException
from Dtos.Historial.HistorialCreateDto import HistorialCreateDto
from Dtos.Historial.HistorialDto import HistorialDto
from Services.HistorialService import HistorialService
from typing import List

historial_router = APIRouter(prefix="/historial", tags=["Historial"])

@historial_router.post("/", response_model=HistorialDto)
def registrar_historial(item: HistorialCreateDto):
    return HistorialService.registrar(item.dict())

@historial_router.get("/usuario/{usuario_id}", response_model=List[HistorialDto])
def obtener_historial_de_usuario(usuario_id: str):
    return HistorialService.buscar_por_usuario(usuario_id)
