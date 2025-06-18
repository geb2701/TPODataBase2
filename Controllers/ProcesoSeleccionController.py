from fastapi import APIRouter, HTTPException
from typing import List
from Dtos.MensajeRespuesta import MensajeRespuesta
from Dtos.ProcesoSeleccion.ProcesoSeleccionCreateDto import ProcesoSeleccionCreateDto
from Dtos.ProcesoSeleccion.ProcesoSeleccion import ProcesoSeleccion
from Dtos.ProcesoSeleccion.ProcesoSeleccionUpdateDto import ProcesoSeleccionUpdateDto
from Services.ProcesoSeleccionService import ProcesoSeleccionService

procesos_router = APIRouter(prefix="/procesos", tags=["Proceso Selección"])

@procesos_router.post("/", response_model=ProcesoSeleccion)
def crear_proceso(data: ProcesoSeleccionCreateDto):
    try:
        return ProcesoSeleccionService.crear(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")

@procesos_router.get("/", response_model=List[ProcesoSeleccion])
def listar_procesos():
    try:
        return ProcesoSeleccionService.listar()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar procesos: {e}")

@procesos_router.get("/{proceso_id}", response_model=ProcesoSeleccion)
def obtener_proceso(proceso_id: str):
    try:
        proceso = ProcesoSeleccionService.obtener_por_id(proceso_id)
        if not proceso:
            raise HTTPException(status_code=404, detail="Proceso no encontrado")
        return proceso
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ID inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@procesos_router.patch("/{proceso_id}", response_model=ProcesoSeleccion)
def actualizar_proceso(proceso_id: str, data: ProcesoSeleccionUpdateDto):
    try:
        return ProcesoSeleccionService.actualizar(proceso_id, data.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@procesos_router.delete("/{proceso_id}", response_model=MensajeRespuesta)
def eliminar_proceso(proceso_id: str):
    try:
        ProcesoSeleccionService.eliminar(proceso_id)
        return {"mensaje": "Proceso eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
