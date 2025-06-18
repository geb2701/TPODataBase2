from datetime import datetime
from bson import ObjectId
from neo4j import GraphDatabase
from Dtos.Historial import Historial
from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
skills_collection = mongo_db["skills"]


class SkillService:
    @staticmethod
    def mongo_to_model(skill):
        skill["id"] = str(skill["_id"])
        skill.pop("_id", None)
        return skill

    @staticmethod
    def crear(data):
        historial = data.get("historial", [])
        hoy = datetime.today()
        historial.append(Historial(fecha=hoy, mensage="Skill creado").model_dump())
        data["historial"] = historial

        existente = skills_collection.find_one({
            "nombre": data.get("nombre"),
            "nivel": data.get("nivel")
        })
        if existente:
            raise ValueError("Ya existe una skill con el mismo nombre y nivel.")

        result = skills_collection.insert_one(data)
        data["id"] = str(result.inserted_id)

        with neo4j.session() as session:
            session.run(
                """
                CREATE (s:Skill {id: $id, nombre: $nombre, nivel: $nivel, tipo: $tipo})
                """,
                id=data["id"],
                nombre=data.get("nombre"),
                nivel=data.get("nivel"),
                tipo=data.get("tipo"),
            )

            session.run(
                """
                MATCH (nueva:Skill {id: $id}), (otra:Skill)
                WHERE otra.nombre = $nombre AND otra.id <> $id
                WITH nueva, otra
                WHERE toInteger(nueva.nivel) > toInteger(otra.nivel)
                MERGE (nueva)-[:SUPERIOR]->(otra)
                """,
                id=data["id"],
                nombre=data.get("nombre", "")
            )

            session.run(
                """
                MATCH (nueva:Skill {id: $id}), (otra:Skill)
                WHERE otra.nombre = $nombre AND otra.id <> $id
                WITH nueva, otra
                WHERE toInteger(nueva.nivel) < toInteger(otra.nivel)
                MERGE (nueva)-[:INFERIOR]->(otra)
                """,
                id=data["id"],
                nombre=data.get("nombre", "")
            )
        return data

    @staticmethod
    def listar():
        usuarios = list(skills_collection.find())
        return [SkillService.mongo_to_model(u) for u in usuarios]

    @staticmethod
    def obtener_por_id(usuario_id):
        usuario = skills_collection.find_one({"_id": ObjectId(usuario_id)})
        if usuario:
            return SkillService.mongo_to_model(usuario)
        return None
