from bson import ObjectId, errors
from Services import DatabaseConfig
from fastapi import HTTPException

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()

certificaciones_collection = mongo_db["certificaciones"]
cursos_collection = mongo_db["cursos"]
usuarios_collection = mongo_db["usuarios"]

def mongo_to_model(cert):
    cert["id"] = str(cert["_id"])
    cert.pop("_id", None)
    return cert

def validar_usuario_existe(id):
    skill = usuarios_collection.find_one({"_id": ObjectId(id)})
    if not skill:
        raise HTTPException(status_code=500, detail="El ID de usuario no existe.")

def validar_curso_existe(id):
    skill = cursos_collection.find_one({"_id": ObjectId(id)})
    if not skill:
        raise HTTPException(status_code=500, detail="El ID de curso no existe.")

class CertificacionService:
    @staticmethod
    def crear(data):
        validar_usuario_existe(data.get("participante"))
        validar_curso_existe(data.get("curso"))

        # Insertar certificación en MongoDB SIEMPRE
        result = certificaciones_collection.insert_one(data)
        cert_dict = data.copy()
        cert_dict["id"] = str(result.inserted_id)

        if cert_dict.get("aprobada"):
            # Relacionar usuario y curso en Neo4j (TIENE_CERTIFICACION)
            with neo4j.session() as session:
                session.run("""
                    MATCH (u:Usuario {id: $participante})
                    MATCH (c:Curso {id: $curso_id})
                    CREATE (u)-[:TIENE_CERTIFICACION {
                        id: $id,
                        puntaje: $puntaje,
                        aprobada: $aprobada
                    }]->(c)
                """,
                id=cert_dict["id"],
                participante=str(cert_dict["participante"]),
                curso_id=str(cert_dict["curso"]),
                puntaje=cert_dict.get("puntaje"),
                aprobada=cert_dict.get("aprobada"))

            curso = cursos_collection.find_one({"_id": ObjectId(cert_dict["curso"])})
            usuario = usuarios_collection.find_one({"_id": ObjectId(cert_dict["participante"])})

            if curso and usuario:
                skills_curso = curso.get("skills", [])
                skills_usuario = usuario.get("skills", [])
                nuevas_skills = [s for s in skills_curso if s not in skills_usuario]

                if nuevas_skills:
                    usuarios_collection.update_one(
                        {"_id": ObjectId(cert_dict["participante"])},
                        {"$push": {"skills": {"$each": nuevas_skills}}}
                    )
                    with neo4j.session() as session:
                        for skill_id in nuevas_skills:
                            session.run("""
                                MATCH (u:Usuario {id: $usuario_id})
                                MATCH (s:Skill {id: $skill_id})
                                MERGE (u)-[:DOMINA]->(s)
                            """,
                            usuario_id=str(cert_dict["participante"]),
                            skill_id=skill_id)

        else:
            with neo4j.session() as session:
                session.run("""
                    MATCH (u:Usuario {id: $participante})
                    MATCH (c:Curso {id: $curso_id})
                    CREATE (u)-[:INTENTO_FALLIDO {
                        id: $id,
                        puntaje: $puntaje,
                        aprobada: $aprobada
                    }]->(c)
                """,
                id=cert_dict["id"],
                participante=str(cert_dict["participante"]),
                curso_id=str(cert_dict["curso"]),
                puntaje=cert_dict.get("puntaje"),
                aprobada=cert_dict.get("aprobada"))))

        cert_dict["curso"] = str(cert_dict["curso"])
        cert_dict["participante"] = str(cert_dict["participante"])
        return cert_dict

    @staticmethod
    def listar():
        certificaciones = list(certificaciones_collection.find())
        return [mongo_to_model(c) for c in certificaciones]

    @staticmethod
    def obtener_por_id(cert_id: str):
        cert = certificaciones_collection.find_one({"_id": cert_id})
        if not cert:
            raise HTTPException(status_code=404, detail="Certificación no encontrada")

        return mongo_to_model(cert)

