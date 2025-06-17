from datetime import date
from datetime import date, datetime
from bson import ObjectId

from Dtos.Historial import Historial
from Services import DatabaseConfig

db_config = DatabaseConfig.DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
usuarios_collection = mongo_db["usuarios"]

def usuario_mongo_to_model(usuario):
    usuario["id"] = str(usuario["_id"])
    usuario.pop("_id", None)
    return usuario

def crear_usuario(usuario_dict):
    historial = usuario_dict.get("historial", [])
    hoy = datetime.today()
    historial.append(Historial(fecha=hoy, mensage="Usuario creado").model_dump())
    usuario_dict["historial"] = historial

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
    return [usuario_mongo_to_model(u) for u in usuarios]

def obtener_usuario(usuario_id):
    usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        return usuario_mongo_to_model(usuario)
    return None

def actualizar_usuario(usuario_id, update_data):
    usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return None

    historial = usuario.get("historial", [])
    hoy = datetime.today()
    for campo, nuevo_valor in update_data.items():
        valor_anterior = usuario.get(campo, None)
        mensaje = f"Se cambió '{campo}' de '{valor_anterior}' a '{nuevo_valor}'"
        historial.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
    update_data["historial"] = historial

    result = usuarios_collection.update_one(
        {"_id": ObjectId(usuario_id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        return None

    usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
    usuario_dto = usuario_mongo_to_model(usuario)
    # Actualizar nodo en Neo4j
    with neo4j.session() as session:
        props = {k: v for k, v in update_data.items() if v is not None and k != "historial"}
        session.run(
            """
            MATCH (u:Usuario {id: $id})
            SET u += $props
            """,
            id=usuario_id,
            props=props
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
        
        if "skills" in update_data and isinstance(update_data["skills"], list):
            for skill_id in update_data["skills"]:
                session.run(
                    """
                    MERGE (s:Skill {id: $skill_id})
                    WITH s
                    MATCH (u:Usuario {id: $usuario_id})
                    MERGE (u)-[:DOMINA]->(s)
                    """,
                    usuario_id=usuario_id,
                    skill_id=skill_id
                )
                
    return usuario_dto