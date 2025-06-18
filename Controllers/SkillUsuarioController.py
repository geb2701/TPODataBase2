from fastapi import APIRouter, HTTPException
from Dtos.MensajeRespuesta import MensajeRespuesta
from Dtos.Usuario.AgregarSkillDto import AgregarSkillDto

from Services.UsuarioServices import UsuarioService

skill_usuario_router = APIRouter(prefix="/usuarios", tags=["Skills de Usuario"])

@skill_usuario_router.patch("/añadir_skill", response_model=MensajeRespuesta)
def añadir_skill_endpoint(data: AgregarSkillDto):
    try:
        usuario = UsuarioService.obtener_por_id(data.usuarioId)

        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        usuario.setdefault("skills", [])

        if data.skillId in usuario["skills"]:
            raise HTTPException(status_code=400, detail="La skill ya está asociada")

        usuario["skills"].append(data.skillId)

        UsuarioService.actualizar(data.usuarioId, {"skills": usuario["skills"]})

        return {"message": "Skill añadida correctamente"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
