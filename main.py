from fastapi import FastAPI, APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from Controllers.SkillController import skills_router
from Controllers.UsuarioController import usuarios_router
from Controllers.EquipoController import equipo_router
from Controllers.ProcesoSeleccionController import procesos_router
from Controllers.EmpresaController import empresa_router
from Controllers.OfertaController import oferta_router
from Controllers.SkillUsuarioController import skill_usuario_router
from Controllers.ReferenciaUsuarioController import referencia_usuario_router
from Controllers.CursoController import curso_router
from Controllers.CertificacionController import certificacion_router

app = FastAPI()

app.include_router(usuarios_router)
app.include_router(skills_router)
app.include_router(empresa_router)
app.include_router(equipo_router)
app.include_router(skill_usuario_router)
app.include_router(referencia_usuario_router)
app.include_router(curso_router)
app.include_router(certificacion_router)

"""
app.include_router(entrevistas_router)
app.include_router(empresas_router)
app.include_router(busquedas_router)
app.include_router(matches_router)
app.include_router(inscripciones_router)
app.include_router(cursos_router)
app.include_router(recomendaciones_router)
app.include_router(procesos_router)
app.include_router(historial_router)
app.include_router(oferta_router)
"""

app.include_router(certificacion_router)

