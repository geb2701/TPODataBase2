from fastapi import APIRouter, HTTPException
from typing import List
from Services.EmpresaService import EmpresaService
from Dtos.Empresa.EmpresaCreateDto import EmpresaCreateDto
from Dtos.Empresa.Empresa import Empresa
from Dtos.Empresa.EmpresaUpdateDto import EmpresaUpdateDto

empresa_router = APIRouter(prefix="/empresas", tags=["Empresas"])

@empresa_router.post("/", response_model=Empresa)
def crear_empresa(data: EmpresaCreateDto):
    try:
        return EmpresaService.crear(data.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@empresa_router.get("/", response_model=List[Empresa])
def listar_empresas():
    try:
        return EmpresaService.listar()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@empresa_router.get("/{empresa_id}", response_model=Empresa)
def obtener_empresa(empresa_id: str):
    try:
        empresa = EmpresaService.obtener_por_id(empresa_id)
        if not empresa:
            raise HTTPException(404, "Empresa no encontrada")
        return empresa
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@empresa_router.patch("/{empresa_id}", response_model=Empresa)
def actualizar_empresa(empresa_id: str, data: EmpresaUpdateDto):
    try:
        if not EmpresaService.obtener_por_id(empresa_id):
            raise HTTPException(404, "Empresa no encontrada")
        return EmpresaService.actualizar(empresa_id, data.dict(exclude_unset=True))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@empresa_router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: str):
    try:
        if not EmpresaService.obtener_por_id(empresa_id):
            raise HTTPException(404, "Empresa no encontrada")
        EmpresaService.eliminar(empresa_id)
        return {"mensaje": "Empresa eliminada"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))