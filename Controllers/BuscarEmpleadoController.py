from fastapi import APIRouter, HTTPException
from typing import Dict

from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()

buscar_empleado_router = APIRouter(prefix="/buscarEmpleado", tags=["Buscar Empleado"])

@buscar_empleado_router.get("/{oferta_id}", response_model=Dict[int, list])
def buscar_empleados_para_oferta(oferta_id: str):
    query = """
    MATCH (oferta:Oferta {id: $ofertaId})-[:REQUIERE]->(skillReq:Skill)
    WITH oferta, collect(skillReq) AS skillsRequeridos

    UNWIND skillsRequeridos AS skillReq
    MATCH (skillSup:Skill)
    WHERE skillSup.tipo = skillReq.tipo AND skillSup.nivel >= skillReq.nivel

    WITH collect(DISTINCT skillSup.id) AS skillIds

    MATCH (usuario:Usuario)-[:POSEE]->(skill:Skill)
    WHERE skill.id IN skillIds

    WITH usuario, count(DISTINCT skill.id) AS matchCount
    ORDER BY matchCount DESC

    WITH matchCount, collect(usuario.id) AS usuarios
    RETURN apoc.map.fromPairs(collect([matchCount, usuarios])) AS resultado
    """
    try:
        result = Neo4jService.run_query(query, {"ofertaId": oferta_id})
        if result and "resultado" in result[0]:
            return result[0]["resultado"]
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando la consulta: {e}")