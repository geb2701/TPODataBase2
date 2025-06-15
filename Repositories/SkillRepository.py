from pymongo import MongoClient
from bson import ObjectId

from Services import DatabaseConfig

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
skills_collection = mongo_db["skills"]

def skill_mongo_to_dto(skill):
    skill["id"] = str(skill["_id"])
    skill.pop("_id", None)
    return skill

def crear_skill(skill_dict):
    result = skills_collection.insert_one(skill_dict)
    skill_dict["id"] = str(result.inserted_id)
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
    result = skills_collection.update_one(
        {"_id": ObjectId(skill_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        return None
    skill = skills_collection.find_one({"_id": ObjectId(skill_id)})
    return skill_mongo_to_dto(skill)

def eliminar_skill(skill_id):
    result = skills_collection.delete_one({"_id": ObjectId(skill_id)})
    return result.deleted_count > 0