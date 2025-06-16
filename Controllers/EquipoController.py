from fastapi import APIRouter, HTTPException
from typing import List
from Services.EquipoService import EquipoService
from Dtos.Equipo.EquipoDto import EquipoDto
from Dtos.Equipo.EquipoCreateDto import EquipoCreateDto
from Dtos.Equipo.EquipoUpdateDto import EquipoUpdateDto

equipo_router = APIRouter(prefix="/equipos", tags=["Equipos"])

@equipo_router.post("/", response_model=EquipoDto)
def crear_equipo(data: EquipoCreateDto):
    return EquipoService.crear(data.dict())

@equipo_router.get("/", response_model=List[EquipoDto])
def listar_equipos():
    return EquipoService.listar()

@equipo_router.get("/{equipo_id}", response_model=EquipoDto)
def obtener_equipo(equipo_id: str):
    equipo = EquipoService.obtener_por_id(equipo_id)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    return equipo

@equipo_router.patch("/{equipo_id}", response_model=EquipoDto)
def actualizar_equipo(equipo_id: str, data: EquipoUpdateDto):
    if not EquipoService.obtener_por_id(equipo_id):
        raise HTTPException(404, "Equipo no encontrado")
    return EquipoService.actualizar(equipo_id, data.dict(exclude_unset=True))

@equipo_router.delete("/{equipo_id}")
def eliminar_equipo(equipo_id: str):
    if not EquipoService.obtener_por_id(equipo_id):
        raise HTTPException(404, "Equipo no encontrado")
    EquipoService.eliminar(equipo_id)
    return {"mensaje": "Equipo eliminado"}
