from fastapi import APIRouter, HTTPException
from typing import Dict

from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()
neo4j = db_config.get_neo4j_driver()

buscar_empleado_router = APIRouter(prefix="/buscarEmpleado", tags=["Buscar Empleado"])

@buscar_empleado_router.get("/{oferta_id}", response_model=Dict[int, list])
def buscar_empleados_para_oferta(oferta_id: str):
    query = """
    MATCH (oferta:Oferta {id: "68525752a622bd1341cfcd42"})-[:REQUIERE]->(skillReq:Skill)

    WITH collect(skillReq) AS skillsRequeridas

    UNWIND skillsRequeridas AS skillReq
    OPTIONAL MATCH (skillSup:Skill)-[:SUPERIOR*0..]->(skillReq)
    WHERE skillSup.tipo = skillReq.tipo AND skillSup.nivel >= skillReq.nivel

    WITH collect(DISTINCT skillSup.id) AS skillIds

    MATCH (usuario:Usuario)-[:DOMINA]->(skill:Skill)
    WHERE skill.id IN skillIds

    WITH usuario, count(DISTINCT skill.id) AS matchCount
    ORDER BY matchCount DESC

    WITH matchCount, collect(usuario.id) AS usuarios
    RETURN apoc.map.fromPairs(collect([matchCount, usuarios])) AS resultado
    """
    try:
        with neo4j.session() as session:
            result = session.run(query, {"ofertaId": oferta_id})
            records = list(result)
            if records:
                resultado = records[0].get("resultado")
                if resultado:
                    return resultado
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando la consulta: {e}")
    

@buscar_empleado_router.get("/{oferta_id}/recomendados", response_model=Dict[int, list])
def buscar_empleados_para_oferta(oferta_id: str):
    query = """
        MATCH (oferta:Oferta {id: $ofertaId})-[:REQUIERE]->(skillReq:Skill)
        WITH oferta, collect(skillReq) AS skillsRequeridas

        UNWIND skillsRequeridas AS skillReq
        OPTIONAL MATCH (skillSup:Skill)-[:SUPERIOR*0..]->(skillReq)
        WHERE skillSup.tipo = skillReq.tipo AND skillSup.nivel >= skillReq.nivel
        WITH oferta, collect(DISTINCT skillSup.id) AS skillIds

        MATCH (empresa:Empresa)-[:PUBLICA]->(oferta)
        MATCH (empresa)-[:TIENE_EQUIPO]->(equipo:Equipo)
        MATCH (usuarioEquipo:Usuario)-[:PERTENECE_A]->(equipo)
        WITH skillIds, collect(DISTINCT usuarioEquipo) AS usuariosEquipo

        UNWIND usuariosEquipo AS usuarioEquipo
        MATCH (usuarioEquipo)-[:REFIERE_A]->(usuarioRecomendado:Usuario)
        WITH skillIds, collect(DISTINCT usuarioRecomendado) AS usuariosRecomendados

        UNWIND usuariosRecomendados AS usuario
        MATCH (usuario)-[:DOMINA]->(skill:Skill)
        WHERE skill.id IN skillIds
        WITH usuario, count(DISTINCT skill.id) AS matchCount
        ORDER BY matchCount DESC

        WITH matchCount, collect(usuario.id) AS usuarios
        RETURN apoc.map.fromPairs(collect([matchCount, usuarios])) AS resultado
    """
    try:
        with neo4j.session() as session:
            result = session.run(query, {"ofertaId": oferta_id})
            records = list(result)
            if records:
                resultado = records[0].get("resultado")
                if resultado:
                    return resultado
            return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando la consulta: {e}")