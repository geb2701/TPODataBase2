from fastapi import FastAPI, APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional

from Dtos.Usuario.UsuarioCreateDto import UsuarioCreateDto
from Dtos.Usuario.UsuarioDto import UsuarioDto
from Dtos.Usuario.UsuarioUpdateDto import UsuarioUpdateDto
from Dtos.Usuario.ReferirDto import ReferirDto

usuarios_router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

#temporal
db_usuarios = {}

@usuarios_router.post("/", response_model=UsuarioDto)
def crear_usuario(usuario: UsuarioCreateDto):
    user_id = str(len(db_usuarios) + 1)
    db_usuarios[user_id] = usuario.dict()
    return db_usuarios[user_id]

@usuarios_router.get("/", response_model=List[UsuarioDto])
def listar_usuarios():
    return list(db_usuarios.values())

@usuarios_router.get("/{usuario_id}", response_model=UsuarioDto)
def obtener_usuario(usuario_id: str):
    usuario = db_usuarios.get(usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    return usuario

@usuarios_router.patch("/{usuario_id}", response_model=UsuarioDto)
def actualizar_usuario(usuario_id: str, usuario_update: UsuarioUpdateDto):
    usuario = db_usuarios.get(usuario_id)
    if not usuario:
        raise HTTPException(404, "Usuario no encontrado")
    update_data = usuario_update.dict(exclude_unset=True)
    usuario.update(update_data)
    db_usuarios[usuario_id] = usuario
    return usuario

@usuarios_router.patch("/referir")
def referir_usuario(data: ReferirDto):
    return {"message": "Usuario referido correctamente"}
