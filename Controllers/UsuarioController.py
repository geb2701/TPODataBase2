from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from Dtos.Usuario.UsuarioCreateDto import UsuarioCreateDto
from Dtos.Usuario.Usuario import Usuario
from Dtos.Usuario.UsuarioUpdateDto import UsuarioUpdateDto
from Dtos.Usuario.ReferirDto import ReferirDto
from Dtos.Usuario.AgregarSkillDto import AgregarSkillDto
from Dtos.Usuario.UsuarioFilterDto import UsuarioFilterDto

from Services.UsuarioServices import UsuarioService

usuarios_router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@usuarios_router.post("/", response_model=Usuario)
def crear_usuario_endpoint(usuario: UsuarioCreateDto):
    try:
        return UsuarioService.crear(usuario.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@usuarios_router.get("/", response_model=List[Usuario])
def listar_usuarios_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filtros: UsuarioFilterDto = Depends()
):
    try:
        usuarios = UsuarioService.listar()
        for field, value in filtros.model_dump(exclude_none=True).items():
            usuarios = [u for u in usuarios if u.get(field) == value]
        return usuarios[skip:skip + limit]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@usuarios_router.get("/{usuario_id}", response_model=Usuario)
def obtener_usuario_endpoint(usuario_id: str):
    try:
        usuario = UsuarioService.obtener_por_id(usuario_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")
        return usuario
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@usuarios_router.patch("/{usuario_id}", response_model=Usuario)
def actualizar_usuario_endpoint(usuario_id: str, usuario_update: UsuarioUpdateDto):
    try:
        update_data = {k: v for k, v in usuario_update.model_dump(exclude_unset=True).items() if v is not None}
        usuario = UsuarioService.actualizar(usuario_id, update_data)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")
        return usuario
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))