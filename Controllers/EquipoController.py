from fastapi import APIRouter, HTTPException
from typing import List
from Services.EquipoService import EquipoService
from Dtos.Equipo.EquipoDto import EquipoDto
from Dtos.Equipo.EquipoCreateDto import EquipoCreateDto
from Dtos.Equipo.EquipoUpdateDto import EquipoUpdateDto
from fastapi import Query, Depends
from Dtos.Equipo.EquipoFilterDto import EquipoFilterDto

equipo_router = APIRouter(prefix="/equipos", tags=["Equipos"])

@equipo_router.post("/", response_model=EquipoDto)
def crear_equipo(data: EquipoCreateDto):
    try:
        return EquipoService.crear(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al crear equipo")


@equipo_router.get("/", response_model=List[EquipoDto])
def listar_equipos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filtros: EquipoFilterDto = Depends()
):
    try:
        equipos = EquipoService.listar()
        for field, value in filtros.model_dump(exclude_none=True).items():
            equipos = [e for e in equipos if e.get(field) == value]
        return equipos[skip:skip + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al listar equipos")


@equipo_router.get("/{equipo_id}", response_model=EquipoDto)
def obtener_equipo(equipo_id: str):
    try:
        equipo = EquipoService.obtener_por_id(equipo_id)
        if not equipo:
            raise HTTPException(status_code=404, detail="Equipo no encontrado")
        return equipo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al obtener equipo")


@equipo_router.patch("/{equipo_id}", response_model=EquipoDto)
def actualizar_equipo(equipo_id: str, data: EquipoUpdateDto):
    try:
        return EquipoService.actualizar(equipo_id, data.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al actualizar equipo")


@equipo_router.delete("/{equipo_id}")
def eliminar_equipo(equipo_id: str):
    try:
        if not EquipoService.obtener_por_id(equipo_id):
            raise HTTPException(404, "Equipo no encontrado")
        EquipoService.eliminar(equipo_id)
        return {"mensaje": "Equipo eliminado"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al eliminar equipo")


@equipo_router.patch("/{equipo_id}/remover_integrante/{usuario_id}")
def remover_integrante(equipo_id: str, usuario_id: str):
    try:
        EquipoService.eliminar_integrante(equipo_id, usuario_id)
        return {"message": "Integrante removido correctamente"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al remover integrante")


@equipo_router.patch("/{equipo_id}/agregar_integrante/{usuario_id}")
def agregar_integrante(equipo_id: str, usuario_id: str):
    try:
        equipo = EquipoService.agregar_integrante(equipo_id, usuario_id)
        return {"message": "Integrante agregado correctamente", "equipo": equipo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error al agregar integrante")
