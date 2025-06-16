from pymongo import MongoClient
from bson import ObjectId
from Services import DatabaseConfig
from fastapi import HTTPException
from datetime import date


db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
certificaciones_collection = mongo_db["certificaciones"]

def certificacion_mongo_to_dto(cert):
    cert["id"] = str(cert["_id"])
    cert.pop("_id", None)
    return cert

def crear(cert_dict):
    try:
        result = certificaciones_collection.insert_one(cert_dict)
        cert_dict["id"] = str(result.inserted_id)

        with neo4j.session() as session:
            session.run("""
                MATCH (u:Usuario {id: $usuario_id})
                MATCH (c:Curso {id: $curso_id})
                CREATE (u)-[:TIENE_CERTIFICACION {
                    puntaje: $puntaje,
                    aprobada: $aprobada,
                    fecha_emision: $fecha_emision
                }]->(c)
            """,
            usuario_id=cert_dict["participante"],
            curso_id=cert_dict["curso"],
            puntaje=cert_dict["puntaje"],
            aprobada=cert_dict["aprobada"],
            fecha_emision=str(cert_dict["fecha_emision"])
        )

        return cert_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def listar():
    try:
        certificaciones = list(certificaciones_collection.find())
        return [certificacion_mongo_to_dto(c) for c in certificaciones]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))