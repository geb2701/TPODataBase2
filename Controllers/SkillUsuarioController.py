from fastapi import APIRouter, HTTPException
from Dtos.Usuario.AgregarSkillDto import AgregarSkillDto
from Repositories.UsuarioRepository import obtener_usuario, actualizar_usuario

skill_usuario_router = APIRouter(prefix="/usuarios", tags=["Skills de Usuario"])

@skill_usuario_router.patch("/añadir_skill")
def añadir_skill_endpoint(data: AgregarSkillDto):
    try:
        usuario = obtener_usuario(data.usuarioId)

        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        usuario.setdefault("skills", [])

        if data.skillId in usuario["skills"]:
            raise HTTPException(status_code=400, detail="La skill ya está asociada")

        usuario["skills"].append(data.skillId)

        actualizar_usuario(data.usuarioId, {"skills": usuario["skills"]})

        return {"message": "Skill añadida correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
