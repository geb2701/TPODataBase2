from pymongo import MongoClient
from bson import ObjectId

from Services import DatabaseConfig

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
skills_collection = mongo_db["skills"]

def skill_mongo_to_dto(skill):
    skill["id"] = str(skill["_id"])
    skill.pop("_id", None)
    return skill

def crear_skill(skill_dict):
    existente = skills_collection.find_one({
        "nombre": skill_dict.get("nombre"),
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
    return [skill_mongo_to_dto(s) for s in skills]

def obtener_skill(skill_id):
    skill = skills_collection.find_one({"_id": ObjectId(skill_id)})
    if skill:
        return skill_mongo_to_dto(skill)
    return None

def actualizar_skill(skill_id, update_data):
    if "nombre" in update_data and "nivel" in update_data:
        existente = skills_collection.find_one({
            "nombre": update_data["nombre"],
            "nivel": update_data["nivel"],
            "_id": {"$ne": ObjectId(skill_id)}
        })
        if existente:
            raise ValueError("Ya existe otra skill con el mismo nombre y nivel.")
    result = skills_collection.update_one(
        {"_id": ObjectId(skill_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        return None
    skill = skills_collection.find_one({"_id": ObjectId(skill_id)})
    with neo4j.session() as session:
        session.run(
            """
            MATCH (s:Skill {id: $id})
            SET s += $props
            """,
            id=skill_id,
            props={k: v for k, v in update_data.items() if v is not None}
        )
    return skill_mongo_to_dto(skill)

def eliminar_skill(skill_id):
    result = skills_collection.delete_one({"_id": ObjectId(skill_id)})
    eliminado = result.deleted_count > 0
    if eliminado:
        # Eliminar nodo en Neo4j
        with neo4j.session() as session:
            session.run(
                """
                MATCH (s:Skill {id: $id})
                DETACH DELETE s
                """,
                id=skill_id
            )
    return result.deleted_count > 0