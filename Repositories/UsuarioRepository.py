from pymongo import MongoClient
from bson import ObjectId
from neo4j import GraphDatabase

from Services import DatabaseConfig

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
usuarios_collection = mongo_db["usuarios"]

"""
try:
    neo4j = GraphDatabase.driver(
        "neo4j+s://bd136a15.databases.neo4j.io",
        auth=("neo4j", "0czpIif4DzPnO1prJ8QjyfSBHut1LKTo2ZeX-Y4rndQ")
    )
    neo4j.verify_connectivity()
except Exception as e:
    print(f"Error conectando a Neo4j: {e}")
    neo4j = None

neo4j = GraphDatabase.driver(
    "neo4j+s://bd136a15.databases.neo4j.io",
    auth=("neo4j", "0czpIif4DzPnO1prJ8QjyfSBHut1LKTo2ZeX-Y4rndQ")
)
neo4j.verify_connectivity()
"""

def usuario_mongo_to_dto(usuario):
    usuario["id"] = str(usuario["_id"])
    usuario.pop("_id", None)
    return usuario

def crear_usuario(usuario_dict):
    result = usuarios_collection.insert_one(usuario_dict)
    usuario_dict["id"] = str(result.inserted_id)
    # Crear nodo en Neo4j
    with neo4j.session() as session:
        session.run(
            """
            CREATE (u:Usuario {id: $id, nombre: $nombre, email: $email})
            """,
            id=usuario_dict["id"],
            nombre=usuario_dict.get("nombre", ""),
            email=usuario_dict.get("email", "")
        )
    return usuario_dict

def listar_usuarios():
    usuarios = list(usuarios_collection.find())
    return [usuario_mongo_to_dto(u) for u in usuarios]

def obtener_usuario(usuario_id):
    usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        return usuario_mongo_to_dto(usuario)
    return None

def actualizar_usuario(usuario_id, update_data):
    result = usuarios_collection.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        return None
    usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
    usuario_dto = usuario_mongo_to_dto(usuario)
    # Actualizar nodo en Neo4j
    with neo4j.session() as session:
        session.run(
            """
            MATCH (u:Usuario {id: $id})
            SET u += $props
            """,
            id=usuario_id,
            props={k: v for k, v in update_data.items() if v is not None}
        )
        
        if "recomendado" in update_data and isinstance(update_data["recomendado"], list):
            for recomendado_id in update_data["recomendado"]:
                session.run(
                    """
                    MATCH (a:Usuario {id: $recomendador_id}), (b:Usuario {id: $recomendado_id})
                    MERGE (a)-[:REFIERE_A]->(b)
                    """,
                    recomendador_id=usuario_id,
                    recomendado_id=recomendado_id
                )
    return usuario_dto