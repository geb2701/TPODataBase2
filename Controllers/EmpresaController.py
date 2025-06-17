from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from Services.EmpresaService import EmpresaService
from Dtos.Empresa.EmpresaCreateDto import EmpresaCreateDto
from Dtos.Empresa.Empresa import Empresa
from Dtos.Empresa.EmpresaUpdateDto import EmpresaUpdateDto
from Dtos.Empresa.EmpresaFilterDto import EmpresaFilterDto

empresa_router = APIRouter(prefix="/empresas", tags=["Empresas"])


@empresa_router.post("/", response_model=Empresa)
def crear_empresa(data: EmpresaCreateDto):
    try:
        return EmpresaService.crear(data.model_dump())
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error en los datos: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear empresa: {e}")


@empresa_router.get("/", response_model=List[Empresa])
def listar_empresas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    filtros: EmpresaFilterDto = Depends()
):
    try:
        empresas = EmpresaService.listar()
        filtros_dict = filtros.model_dump(exclude_none=True)

        for field, value in filtros_dict.items():
            empresas = [e for e in empresas if e.get(field) == value]

        return empresas[skip:skip + limit]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar empresas: {e}")


@empresa_router.get("/{empresa_id}", response_model=Empresa)
def obtener_empresa(empresa_id: str):
    try:
        empresa = EmpresaService.obtener_por_id(empresa_id)
        if not empresa:
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return empresa
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ID inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener empresa: {e}")


@empresa_router.patch("/{empresa_id}", response_model=Empresa)
def actualizar_empresa(empresa_id: str, data: EmpresaUpdateDto):
    try:
        if not EmpresaService.obtener_por_id(empresa_id):
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        return EmpresaService.actualizar(empresa_id, data.dict(exclude_unset=True))
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Error de validación: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar empresa: {e}")


@empresa_router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: str):
    try:
        if not EmpresaService.obtener_por_id(empresa_id):
            raise HTTPException(status_code=404, detail="Empresa no encontrada")
        EmpresaService.eliminar(empresa_id)
        return {"mensaje": "Empresa eliminada"}
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ID inválido: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar empresa: {e}")
