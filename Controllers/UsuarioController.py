from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List

from Dtos.Usuario.UsuarioCreateDto import UsuarioCreateDto
from Dtos.Usuario.Usuario import Usuario
from Dtos.Usuario.UsuarioUpdateDto import UsuarioUpdateDto
from Dtos.Usuario.ReferirDto import ReferirDto
from Dtos.Usuario.AgregarSkillDto import AgregarSkillDto
from Dtos.Usuario.UsuarioFilterDto import UsuarioFilterDto

from Repositories.UsuarioRepository import (
    crear_usuario,
    listar_usuarios,
    obtener_usuario,
    actualizar_usuario
)

usuarios_router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@usuarios_router.post("/", response_model=Usuario)
def crear_usuario_endpoint(usuario: UsuarioCreateDto):
    try:
        return crear_usuario(usuario.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@usuarios_router.get("/", response_model=List[Usuario])
def listar_usuarios_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filtros: UsuarioFilterDto = Depends()
):
    try:
        usuarios = listar_usuarios()
        # Filtrado automático usando los campos no nulos del DTO
        for field, value in filtros.model_dump(exclude_none=True).items():
            usuarios = [u for u in usuarios if u.get(field) == value]
        return usuarios[skip:skip + limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@usuarios_router.get("/{usuario_id}", response_model=Usuario)
def obtener_usuario_endpoint(usuario_id: str):
    try:
        usuario = obtener_usuario(usuario_id)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
@usuarios_router.patch("/referir", response_model=str)
def referir_usuario_endpoint(data: ReferirDto):
    try:
        recomendador = obtener_usuario(data.recomendadorId)
        referido = obtener_usuario(data.referidoId)

        if not recomendador or not referido:
            raise HTTPException(404, "Uno o ambos usuarios no existen")

        # Inicializar listas si no existen
        recomendador.setdefault("recomendado", [])
        referido.setdefault("referido", [])

        # Validar si ya existe la relación
        if data.referidoId in recomendador["recomendado"]:
            raise HTTPException(status_code=500, detail=str(e))

        # Añadir la relación
        recomendador["recomendado"].append(data.referidoId)
        referido["referido"].append(data.recomendadorId)

        actualizar_usuario(data.recomendadorId, {"recomendado": recomendador["recomendado"]})
        actualizar_usuario(data.referidoId, {"referido": referido["referido"]})

        return {"message": "Usuario referido correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@usuarios_router.patch("/añadir_skill")
def añadir_skill_endpoint(data: AgregarSkillDto):
    try:
        usuario = obtener_usuario(data.usuarioId)

        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        usuario.setdefault("skills", [])

        if data.skillId in usuario["skills"]:
            raise HTTPException(status_code=500, detail=str(e))

        usuario["skills"].append(data.skillId)

        actualizar_usuario(data.usuarioId, {"skills": usuario["skills"]})

        return {"message": "Skill añadida correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    """

@usuarios_router.patch("/{usuario_id}", response_model=Usuario)
def actualizar_usuario_endpoint(usuario_id: str, usuario_update: UsuarioUpdateDto):
    try:
        update_data = {k: v for k, v in usuario_update.model_dump(exclude_unset=True).items() if v is not None}
        usuario = actualizar_usuario(usuario_id, update_data)
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))