from pymongo import MongoClient
from bson import ObjectId
from Services import DatabaseConfig

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
curso_collection = mongo_db["cursos"]

def curso_mongo_to_dto(curso):
    curso["id"] = str(curso["_id"])
    curso.pop("_id", None)
    return curso

def crear(curso_dict):
    result = curso_collection.insert_one(curso_dict)
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
    return curso_dict

def listar():
    cursos = list(curso_collection.find())
    return [curso_mongo_to_dto(c) for c in cursos]

def obtener_por_id(curso_id):
    curso = curso_collection.find_one({"_id": ObjectId(curso_id)})
    if curso:
        return curso_mongo_to_dto(curso)
    return None

def actualizar(curso_id, update_data):
    result = curso_collection.update_one(
        {"_id": ObjectId(curso_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        return None

    curso = curso_collection.find_one({"_id": ObjectId(curso_id)})
    with neo4j.session() as session:
        session.run("""
            MATCH (c:Curso {id: $id})
            SET c += $props
        """, id=curso_id, props=update_data)
    return curso_mongo_to_dto(curso)

def eliminar(curso_id):
    result = curso_collection.delete_one({"_id": ObjectId(curso_id)})
    if result.deleted_count > 0:
        with neo4j.session() as session:
            session.run("MATCH (c:Curso {id: $id}) DETACH DELETE c", id=curso_id)
        return True
    return False

