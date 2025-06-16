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
    try:
        equipo = EquipoService.obtener_por_id(equipo_id)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@equipo_router.patch("/{equipo_id}", response_model=EquipoDto)
def actualizar_equipo(equipo_id: str, data: EquipoUpdateDto):
    try:
        return EquipoService.actualizar(equipo_id, data.dict(exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@equipo_router.delete("/{equipo_id}")
def eliminar_equipo(equipo_id: str):
    if not EquipoService.obtener_por_id(equipo_id):
        raise HTTPException(404, "Equipo no encontrado")
    EquipoService.eliminar(equipo_id)
    return {"mensaje": "Equipo eliminado"}

@equipo_router.patch("/{equipo_id}/remover_integrante/{usuario_id}")
def remover_integrante(equipo_id: str, usuario_id: str):
    try:
        EquipoService.eliminar_integrante(equipo_id, usuario_id)
        return {"message": "Integrante removido correctamente"}
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail="Error interno")

@equipo_router.patch("/{equipo_id}/agregar_integrante/{usuario_id}")
def agregar_integrante(equipo_id: str, usuario_id: str):
    try:
        equipo = EquipoService.agregar_integrante(equipo_id, usuario_id)
        return {"message": "Integrante agregado correctamente", "equipo": equipo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))