from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
from Dtos.Historial import Historial
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

def crear(data):
    historial = data.get("historial", [])
    hoy = datetime.today()
    historial.append(Historial(fecha=hoy, mensage="Usuario creado").model_dump())
    data["historial"] = historial

    validar_skills_existen(data.get("skills", []))

    result = cursos_collection.insert_one(data)
    data["id"] = str(result.inserted_id)

    with neo4j.session() as session:
        session.run("""
            CREATE (c:Curso {
                id: $id, titulo: $titulo, descripcion: $descripcion, categoria: $categoria,
                nivel: $nivel, modalidad: $modalidad,
                duracion_horas: $duracion_horas
            })
        """,
        id=str(data["id"]),
        titulo=data.get("titulo", ""),
        descripcion=data.get("descripcion", ""),
        categoria=data.get("categoria", ""),
        nivel=data.get("nivel", ""),
        modalidad=data.get("modalidad", ""),
        duracion_horas=data.get("duracion_horas", 0)
        )

        for skill_id in data.get("skills", []):
            session.run("""
                MATCH (c:Curso {id: $curso_id}), (s:Skill {id: $skill_id})
                MERGE (c)-[:CAPACITA]->(s)
            """, curso_id=data["id"], skill_id=skill_id)

    return data

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