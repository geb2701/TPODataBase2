from pymongo import MongoClient
from bson import ObjectId
from Services import DatabaseConfig
from fastapi import HTTPException

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
cursos_collection = mongo_db["cursos"]
skills_collection = mongo_db["skills"]

def mongo_to_model(curso):
    curso["id"] = str(curso["_id"])
    curso.pop("_id", None)
    return curso

def validar_skills_existen(skills_ids):
    if not skills_ids:
        return
    existentes = list(skills_collection.find({"_id": {"$in": [ObjectId(s) for s in skills_ids]}}))
    if len(existentes) != len(skills_ids):
        raise HTTPException(status_code=500, detail="Uno o más IDs de skills no existen.")

def crear(curso_dict):
    try:
        validar_skills_existen(curso_dict.get("skills", []))

        result = cursos_collection.insert_one(curso_dict)
        curso_dict["id"] = str(result.inserted_id)

        with neo4j.session() as session:
            session.run("""
                CREATE (c:Curso {
                    id: $id, titulo: $titulo, categoria: $categoria,
                    nivel: $nivel, modalidad: $modalidad,
                    duracion_horas: $duracion_horas,
                    fecha_publicacion: $fecha_publicacion,
                    activo: $activo
                })
            """, **curso_dict)

            for skill_id in curso_dict.get("skills", []):
                session.run("""
                    MATCH (c:Curso {id: $curso_id}), (s:Skill {id: $skill_id})
                    MERGE (c)-[:PROPORCIONA]->(s)
                """, curso_id=curso_dict["id"], skill_id=skill_id)

        return curso_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def listar():
    try:
        cursos = list(cursos_collection.find())
        for curso in cursos:
            curso["skills_detalle"] = []
            for skill_id in curso.get("skills", []):
                skill = skills_collection.find_one({"_id": ObjectId(skill_id)})
                if skill:
                    skill["id"] = str(skill["_id"])
                    skill.pop("_id", None)
                    curso["skills_detalle"].append(skill)
        return [mongo_to_model(c) for c in cursos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def obtener_por_id(curso_id):
    try:
        curso = cursos_collection.find_one({"_id": ObjectId(curso_id)})
        if curso:
            curso["skills_detalle"] = []
            for skill_id in curso.get("skills", []):
                skill = skills_collection.find_one({"_id": ObjectId(skill_id)})
                if skill:
                    skill["id"] = str(skill["_id"])
                    skill.pop("_id", None)
                    curso["skills_detalle"].append(skill)
            return mongo_to_model(curso)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def actualizar(curso_id, update_data):
    try:
        validar_skills_existen(update_data.get("skills", []))

        result = cursos_collection.update_one(
            {"_id": ObjectId(curso_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return None

        curso = cursos_collection.find_one({"_id": ObjectId(curso_id)})

        with neo4j.session() as session:
            session.run("""
                MATCH (c:Curso {id: $id})
                SET c += $props
            """, id=curso_id, props=update_data)

            if "skills" in update_data:
                session.run("""
                    MATCH (c:Curso {id: $curso_id})-[r:PROPORCIONA]->()
                    DELETE r
                """, curso_id=curso_id)

                for skill_id in update_data["skills"]:
                    session.run("""
                        MATCH (c:Curso {id: $curso_id}), (s:Skill {id: $skill_id})
                        MERGE (c)-[:PROPORCIONA]->(s)
                    """, curso_id=curso_id, skill_id=skill_id)

        return mongo_to_model(curso)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def eliminar(curso_id):
    try:
        result = cursos_collection.delete_one({"_id": ObjectId(curso_id)})
        eliminado = result.deleted_count > 0
        if eliminado:
            with neo4j.session() as session:
                session.run("""
                    MATCH (c:Curso {id: $id})
                    DETACH DELETE c
                """, id=curso_id)
        return eliminado
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

