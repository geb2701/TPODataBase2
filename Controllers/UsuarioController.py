from fastapi import APIRouter, HTTPException
from typing import List

from Dtos.Usuario.UsuarioCreateDto import UsuarioCreateDto
from Dtos.Usuario.UsuarioDto import UsuarioDto
from Dtos.Usuario.UsuarioUpdateDto import UsuarioUpdateDto
from Dtos.Usuario.ReferirDto import ReferirDto

from Repositories.UsuarioRepository import (
    crear_usuario,
    listar_usuarios,
    obtener_usuario,
    actualizar_usuario
)

usuarios_router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@usuarios_router.post("/", response_model=UsuarioDto)
def crear_usuario_endpoint(usuario: UsuarioCreateDto):
    return crear_usuario(usuario.model_dump())

@usuarios_router.get("/", response_model=List[UsuarioDto])
def listar_usuarios_endpoint():
    return listar_usuarios()

@usuarios_router.get("/{usuario_id}", response_model=UsuarioDto)
def obtener_usuario_endpoint(usuario_id: str):
    usuario = obtener_usuario(usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario

@usuarios_router.patch("/{usuario_id}", response_model=UsuarioDto)
def actualizar_usuario_endpoint(usuario_id: str, usuario_update: UsuarioUpdateDto):
    update_data = {k: v for k, v in usuario_update.model_dump(exclude_unset=True).items() if v is not None}
    usuario = actualizar_usuario(usuario_id, update_data)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario

@usuarios_router.patch("/referir")
def referir_usuario(data: ReferirDto):
    recomendador = obtener_usuario(data.recomendador_id)
    referido = obtener_usuario(data.referido_id)

    if not recomendador or not referido:
        raise HTTPException(404, "Uno o ambos usuarios no existen")

    # Inicializar listas si no existen
    recomendador.setdefault("recomendado", [])
    referido.setdefault("referido", [])

    # Validar si ya existe la relación
    if data.referido_id in recomendador["recomendado"]:
        return {"message": "La relación ya existe"}

    # Añadir la relación
    recomendador["recomendado"].append(data.referido_id)
    referido["referido"].append(data.recomendador_id)

    actualizar_usuario(data.recomendador_id, {"recomendado": recomendador["recomendado"]})
    actualizar_usuario(data.referido_id, {"referido": referido["referido"]})

    return {"message": "Usuario referido correctamente"}