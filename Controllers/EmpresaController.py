from fastapi import APIRouter, HTTPException
from typing import List
from Services.EmpresaService import EmpresaService
from Dtos.Empresa.EmpresaCreateDto import EmpresaCreateDto
from Dtos.Empresa.EmpresaDto import EmpresaDto
from Dtos.Empresa.EmpresaUpdateDto import EmpresaUpdateDto

empresa_router = APIRouter(prefix="/empresas", tags=["Empresas"])

@empresa_router.post("/", response_model=EmpresaDto)
def crear_empresa(data: EmpresaCreateDto):
    return EmpresaService.crear(data.dict())

@empresa_router.get("/", response_model=List[EmpresaDto])
def listar_empresas():
    return EmpresaService.listar()

@empresa_router.get("/{empresa_id}", response_model=EmpresaDto)
def obtener_empresa(empresa_id: str):
    empresa = EmpresaService.obtener_por_id(empresa_id)
    if not empresa:
        raise HTTPException(404, "Empresa no encontrada")
    return empresa

@empresa_router.patch("/{empresa_id}", response_model=EmpresaDto)
def actualizar_empresa(empresa_id: str, data: EmpresaUpdateDto):
    if not EmpresaService.obtener_por_id(empresa_id):
        raise HTTPException(404, "Empresa no encontrada")
    return EmpresaService.actualizar(empresa_id, data.dict(exclude_unset=True))

@empresa_router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: str):
    if not EmpresaService.obtener_por_id(empresa_id):
        raise HTTPException(404, "Empresa no encontrada")
    EmpresaService.eliminar(empresa_id)
    return {"mensaje": "Empresa eliminada"}