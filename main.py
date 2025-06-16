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
"""
# --- MODELOS ---
class Entrevista(BaseModel):
    fecha: str
    comentarios: Optional[str] = None
    estado: Optional[str] = None

class Empresa(BaseModel):
    nombre: str
    industria: Optional[str] = None

class Busqueda(BaseModel):
    titulo: str
    descripcion: Optional[str]
    empresa_id: str

class Inscripcion(BaseModel):
    usuario_id: str
    busqueda_id: str

class Curso(BaseModel):
    nombre: str
    estado: Optional[str] = None

class Calificacion(BaseModel):
    curso_id: str
    nota: float

class Recomendacion(BaseModel):
    usuario_id: str
    recomendado_id: str
    comentario: Optional[str] = None

# --- ROUTERS ---

entrevistas_router = APIRouter(prefix="/entrevistas", tags=["Entrevistas"])
empresas_router = APIRouter(prefix="/empresas", tags=["Empresas"])
busquedas_router = APIRouter(prefix="/busquedas", tags=["Búsquedas"])
matches_router = APIRouter(prefix="/matches", tags=["Matches"])
inscripciones_router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])
cursos_router = APIRouter(prefix="/cursos", tags=["Cursos"])
recomendaciones_router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])

# --- "Bases de datos" en memoria ---

db_usuarios = {}
db_entrevistas = {}
db_empresas = {}
db_busquedas = {}
db_inscripciones = {}
db_cursos = {}
db_recomendaciones = {}

# --- ENTREVISTAS ---

@entrevistas_router.post("/{usuario_id}", response_model=Entrevista)
def añadir_entrevista(usuario_id: str, entrevista: Entrevista):
    entrevista_id = str(len(db_entrevistas) + 1)
    db_entrevistas[entrevista_id] = entrevista.dict()
    # Asociar a usuario_id en Mongo real
    return db_entrevistas[entrevista_id]

@entrevistas_router.get("/{usuario_id}/{entrevista_id}", response_model=Entrevista)
def obtener_entrevista(usuario_id: str, entrevista_id: str):
    entrevista = db_entrevistas.get(entrevista_id)
    if not entrevista:
        raise HTTPException(404, "Entrevista no encontrada")
    return entrevista

@entrevistas_router.patch("/{usuario_id}/{entrevista_id}", response_model=Entrevista)
def actualizar_entrevista(usuario_id: str, entrevista_id: str, entrevista: Entrevista):
    if entrevista_id not in db_entrevistas:
        raise HTTPException(404, "Entrevista no encontrada")
    update_data = entrevista.dict(exclude_unset=True)
    db_entrevistas[entrevista_id].update(update_data)
    return db_entrevistas[entrevista_id]

@entrevistas_router.delete("/{usuario_id}/{entrevista_id}")
def eliminar_entrevista(usuario_id: str, entrevista_id: str):
    if entrevista_id not in db_entrevistas:
        raise HTTPException(404, "Entrevista no encontrada")
    del db_entrevistas[entrevista_id]
    return {"mensaje": "Entrevista eliminada"}

# --- EMPRESAS ---

@empresas_router.post("/", response_model=Empresa)
def crear_empresa(empresa: Empresa):
    empresa_id = str(len(db_empresas) + 1)
    db_empresas[empresa_id] = empresa.dict()
    return db_empresas[empresa_id]

@empresas_router.get("/", response_model=List[Empresa])
def listar_empresas():
    return list(db_empresas.values())

@empresas_router.get("/{empresa_id}", response_model=Empresa)
def obtener_empresa(empresa_id: str):
    empresa = db_empresas.get(empresa_id)
    if not empresa:
        raise HTTPException(404, "Empresa no encontrada")
    return empresa

@empresas_router.patch("/{empresa_id}", response_model=Empresa)
def actualizar_empresa(empresa_id: str, empresa: Empresa):
    if empresa_id not in db_empresas:
        raise HTTPException(404, "Empresa no encontrada")
    update_data = empresa.dict(exclude_unset=True)
    db_empresas[empresa_id].update(update_data)
    return db_empresas[empresa_id]

@empresas_router.delete("/{empresa_id}")
def eliminar_empresa(empresa_id: str):
    if empresa_id not in db_empresas:
        raise HTTPException(404, "Empresa no encontrada")
    del db_empresas[empresa_id]
    return {"mensaje": "Empresa eliminada"}

# --- BÚSQUEDAS ---

@busquedas_router.post("/", response_model=Busqueda)
def crear_busqueda(busqueda: Busqueda):
    busqueda_id = str(len(db_busquedas) + 1)
    db_busquedas[busqueda_id] = busqueda.dict()
    return db_busquedas[busqueda_id]

@busquedas_router.get("/", response_model=List[Busqueda])
def listar_busquedas():
    return list(db_busquedas.values())

@busquedas_router.get("/{busqueda_id}", response_model=Busqueda)
def obtener_busqueda(busqueda_id: str):
    busqueda = db_busquedas.get(busqueda_id)
    if not busqueda:
        raise HTTPException(404, "Búsqueda no encontrada")
    return busqueda

@busquedas_router.patch("/{busqueda_id}", response_model=Busqueda)
def actualizar_busqueda(busqueda_id: str, busqueda: Busqueda):
    if busqueda_id not in db_busquedas:
        raise HTTPException(404, "Búsqueda no encontrada")
    update_data = busqueda.dict(exclude_unset=True)
    db_busquedas[busqueda_id].update(update_data)
    return db_busquedas[busqueda_id]

@busquedas_router.delete("/{busqueda_id}")
def eliminar_busqueda(busqueda_id: str):
    if busqueda_id not in db_busquedas:
        raise HTTPException(404, "Búsqueda no encontrada")
    del db_busquedas[busqueda_id]
    return {"mensaje": "Búsqueda eliminada"}

# --- MATCHES ---

@matches_router.get("/por-busqueda/{busqueda_id}")
def obtener_match(busqueda_id: str):
    # Aquí iría la lógica en Neo4j para obtener candidatos posibles
    return {"mensaje": f"Matches para búsqueda {busqueda_id}"}

@matches_router.get("/recomendacion/{busqueda_id}")
def obtener_match_recomendacion(busqueda_id: str):
    # Lógica con recomendación
    return {"mensaje": f"Matches con recomendación para búsqueda {busqueda_id}"}

# --- INSCRIPCIONES ---

@inscripciones_router.post("/", response_model=Inscripcion)
def crear_inscripcion(inscripcion: Inscripcion):
    inscripcion_id = str(len(db_inscripciones) + 1)
    db_inscripciones[inscripcion_id] = inscripcion.dict()
    return db_inscripciones[inscripcion_id]

@inscripciones_router.get("/", response_model=List[Inscripcion])
def listar_inscripciones():
    return list(db_inscripciones.values())

@inscripciones_router.get("/{inscripcion_id}", response_model=Inscripcion)
def obtener_inscripcion(inscripcion_id: str):
    inscripcion = db_inscripciones.get(inscripcion_id)
    if not inscripcion:
        raise HTTPException(404, "Inscripción no encontrada")
    return inscripcion

@inscripciones_router.patch("/{inscripcion_id}", response_model=Inscripcion)
def actualizar_inscripcion(inscripcion_id: str, inscripcion: Inscripcion):
    if inscripcion_id not in db_inscripciones:
        raise HTTPException(404, "Inscripción no encontrada")
    update_data = inscripcion.dict(exclude_unset=True)
    db_inscripciones[inscripcion_id].update(update_data)
    return db_inscripciones[inscripcion_id]

@inscripciones_router.delete("/{inscripcion_id}")
def eliminar_inscripcion(inscripcion_id: str):
    if inscripcion_id not in db_inscripciones:
        raise HTTPException(404, "Inscripción no encontrada")
    del db_inscripciones[inscripcion_id]
    return {"mensaje": "Inscripción eliminada"}

# --- CURSOS ---

@cursos_router.post("/", response_model=Curso)
def crear_curso(curso: Curso):
    curso_id = str(len(db_cursos) + 1)
    db_cursos[curso_id] = curso.dict()
    return db_cursos[curso_id]

@cursos_router.get("/", response_model=List[Curso])
def listar_cursos():
    return list(db_cursos.values())

@cursos_router.get("/{curso_id}", response_model=Curso)
def obtener_curso(curso_id: str):
    curso = db_cursos.get(curso_id)
    if not curso:
        raise HTTPException(404, "Curso no encontrado")
    return curso

@cursos_router.patch("/{curso_id}", response_model=Curso)
def actualizar_curso(curso_id: str, curso: Curso):
    if curso_id not in db_cursos:
        raise HTTPException(404, "Curso no encontrado")
    update_data = curso.dict(exclude_unset=True)
    db_cursos[curso_id].update(update_data)
    return db_cursos[curso_id]

@cursos_router.delete("/{curso_id}")
def eliminar_curso(curso_id: str):
    if curso_id not in db_cursos:
        raise HTTPException(404, "Curso no encontrado")
    del db_cursos[curso_id]
    return {"mensaje": "Curso eliminado"}

# --- CALIFICACIONES ---

@cursos_router.post("/{curso_id}/calificaciones", response_model=Calificacion)
def agregar_calificacion(curso_id: str, calificacion: Calificacion):
    # Lógica para agregar nota a curso (Mongo/Neo)
    return calificacion

# --- RECOMENDACIONES ---

@recomendaciones_router.post("/", response_model=Recomendacion)
def agregar_recomendacion(recomendacion: Recomendacion):
    rec_id = str(len(db_recomendaciones) + 1)
    db_recomendaciones[rec_id] = recomendacion.dict()
    return db_recomendaciones[rec_id]

@recomendaciones_router.get("/", response_model=List[Recomendacion])
def listar_recomendaciones():
    return list(db_recomendaciones.values())

@recomendaciones_router.get("/{rec_id}", response_model=Recomendacion)
def obtener_recomendacion(rec_id: str):
    rec = db_recomendaciones.get(rec_id)
    if not rec:
        raise HTTPException(404, "Recomendación no encontrada")
    return rec

@recomendaciones_router.patch("/{rec_id}", response_model=Recomendacion)
def actualizar_recomendacion(rec_id: str, recomendacion: Recomendacion):
    if rec_id not in db_recomendaciones:
        raise HTTPException(404, "Recomendación no encontrada")
    update_data = recomendacion.dict(exclude_unset=True)
    db_recomendaciones[rec_id].update(update_data)
    return db_recomendaciones[rec_id]

@recomendaciones_router.delete("/{rec_id}")
def eliminar_recomendacion(rec_id: str):
    if rec_id not in db_recomendaciones:
        raise HTTPException(404, "Recomendación no encontrada")
    del db_recomendaciones[rec_id]
    return {"mensaje": "Recomendación eliminada"}

# --- INCLUIMOS ROUTERS EN LA APP ---
"""
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