from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

from Dtos import Historial
from Services import DatabaseConfig

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
skills_collection = mongo_db["skills"]

def skill_mongo_to_model(skill):
    skill["id"] = str(skill["_id"])
    skill.pop("_id", None)
    return skill

def crear_skill(skill_dict):
    historial = skill_dict.get("historial", [])
    hoy = datetime.today()
    historial.append(Historial(fecha=hoy, mensage="Usuario creado").model_dump())
    skill_dict["historial"] = historial

    existente = skills_collection.find_one({
        "tipo": skill_dict.get("tipo"),
        "nivel": skill_dict.get("nivel")
    })
    if existente:
        raise ValueError("Ya existe una skill con el mismo nombre y nivel.")
    
    result = skills_collection.insert_one(skill_dict)
    skill_dict["id"] = str(result.inserted_id)
    with neo4j.session() as session:
        session.run(
            """
            CREATE (s:Skill {id: $id, nombre: $nombre, nivel: $nivel})
            """,
            id=skill_dict["id"],
            nombre=skill_dict.get("nombre"),
            nivel=skill_dict.get("nivel")
        )
    return skill_dict

def listar_skills():
    skills = list(skills_collection.find())
    return [skill_mongo_to_model(s) for s in skills]
