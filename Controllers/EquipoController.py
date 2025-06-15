from fastapi import APIRouter, HTTPException
from typing import List
from Dtos.Equipo.EquipoCreateDto import EquipoCreateDto
from Dtos.Equipo.EquipoDto import EquipoDto
from Dtos.Equipo.EquipoUpdateDto import EquipoUpdateDto

equipos_router = APIRouter(prefix="/equipos", tags=["Equipos"])

# simulador de base de datos temporal
db_equipos = {}

@equipos_router.post("/", response_model=EquipoDto)
def crear_equipo(equipo: EquipoCreateDto):
    equipo_id = str(len(db_equipos) + 1)
    equipo_data = equipo.dict()
    equipo_data["id"] = equipo_id
    db_equipos[equipo_id] = equipo_data
    return equipo_data

@equipos_router.get("/", response_model=List[EquipoDto])
def listar_equipos():
    return list(db_equipos.values())

@equipos_router.get("/{equipo_id}", response_model=EquipoDto)
def obtener_equipo(equipo_id: str):
    equipo = db_equipos.get(equipo_id)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    return equipo

@equipos_router.patch("/{equipo_id}", response_model=EquipoDto)
def actualizar_equipo(equipo_id: str, datos: EquipoUpdateDto):
    equipo = db_equipos.get(equipo_id)
    if not equipo:
        raise HTTPException(404, "Equipo no encontrado")
    update_data = datos.dict(exclude_unset=True)
    equipo.update(update_data)
    db_equipos[equipo_id] = equipo
    return equipo

@equipos_router.delete("/{equipo_id}")
def eliminar_equipo(equipo_id: str):
    if equipo_id not in db_equipos:
        raise HTTPException(404, "Equipo no encontrado")
    del db_equipos[equipo_id]
    return {"mensaje": "Equipo eliminado"}
