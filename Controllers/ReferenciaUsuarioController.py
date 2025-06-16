from fastapi import APIRouter, HTTPException
from Dtos.Usuario.ReferirDto import ReferirDto
from Repositories.UsuarioRepository import obtener_usuario, actualizar_usuario

referencia_usuario_router = APIRouter(prefix="/usuarios", tags=["Referencias entre Usuarios"])

@referencia_usuario_router.patch("/referir", response_model=str)
def referir_usuario_endpoint(data: ReferirDto):
    try:
        recomendador = obtener_usuario(data.recomendadorId)
        referido = obtener_usuario(data.referidoId)

        if not recomendador or not referido:
            raise HTTPException(404, "Uno o ambos usuarios no existen")

        recomendador.setdefault("recomendado", [])
        referido.setdefault("referido", [])

        if data.referidoId in recomendador["recomendado"]:
            raise HTTPException(status_code=400, detail="Ya existe esta recomendación")

        recomendador["recomendado"].append(data.referidoId)
        referido["referido"].append(data.recomendadorId)

        actualizar_usuario(data.recomendadorId, {"recomendado": recomendador["recomendado"]})
        actualizar_usuario(data.referidoId, {"referido": referido["referido"]})

        return {"message": "Usuario referido correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
