from fastapi import APIRouter, HTTPException
from typing import List
from Dtos.ProcesoSeleccion.ProcesoSeleccionCreateDto import ProcesoSeleccionCreateDto
from Dtos.ProcesoSeleccion.ProcesoSeleccionDto import ProcesoSeleccionDto
from Dtos.ProcesoSeleccion.ProcesoSeleccionUpdateDto import ProcesoSeleccionUpdateDto

procesos_router = APIRouter(prefix="/procesos", tags=["Proceso Selección"])

# Simulador temporal de base de datos
db_procesos = {}

@procesos_router.post("/", response_model=ProcesoSeleccionDto)
def crear_proceso(proceso: ProcesoSeleccionCreateDto):
    proceso_id = str(len(db_procesos) + 1)
    proceso_data = proceso.dict()
    proceso_data["id"] = proceso_id
    db_procesos[proceso_id] = proceso_data
    return proceso_data

@procesos_router.get("/", response_model=List[ProcesoSeleccionDto])
def listar_procesos():
    return list(db_procesos.values())

@procesos_router.get("/{proceso_id}", response_model=ProcesoSeleccionDto)
def obtener_proceso(proceso_id: str):
    proceso = db_procesos.get(proceso_id)
    if not proceso:
        raise HTTPException(404, "Proceso no encontrado")
    return proceso

@procesos_router.patch("/{proceso_id}", response_model=ProcesoSeleccionDto)
def actualizar_proceso(proceso_id: str, datos: ProcesoSeleccionUpdateDto):
    proceso = db_procesos.get(proceso_id)
    if not proceso:
        raise HTTPException(404, "Proceso no encontrado")
    update_data = datos.dict(exclude_unset=True)
    proceso.update(update_data)
    db_procesos[proceso_id] = proceso
    return proceso

@procesos_router.delete("/{proceso_id}")
def eliminar_proceso(proceso_id: str):
    if proceso_id not in db_procesos:
        raise HTTPException(404, "Proceso no encontrado")
    del db_procesos[proceso_id]
    return {"mensaje": "Proceso eliminado"}
