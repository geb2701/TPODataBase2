from bson import ObjectId
from neo4j import GraphDatabase
from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
usuarios_collection = mongo_db["usuarios"]


class UsuarioService:

    @staticmethod
    def _mongo_to_dto(usuario):
        usuario["id"] = str(usuario["_id"])
        usuario.pop("_id", None)
        return usuario

    @staticmethod
    def crear(usuario_dict):
        result = usuarios_collection.insert_one(usuario_dict)
        usuario_dict["id"] = str(result.inserted_id)

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

    @staticmethod
    def listar():
        usuarios = list(usuarios_collection.find())
        return [UsuarioService._mongo_to_dto(u) for u in usuarios]

    @staticmethod
    def obtener_por_id(usuario_id):
        usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
        if usuario:
            return UsuarioService._mongo_to_dto(usuario)
        return None

    @staticmethod
    def actualizar(usuario_id, update_data):
        result = usuarios_collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": update_data}
        )
        if result.matched_count == 0:
            return None

        usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
        usuario_dto = UsuarioService._mongo_to_dto(usuario)

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

            if "skills" in update_data and isinstance(update_data["skills"], list):
                for skill_id in update_data["skills"]:
                    session.run(
                        """
                        MERGE (s:Skill {id: $skill_id})
                        WITH s
                        MATCH (u:Usuario {id: $usuario_id})
                        MERGE (u)-[:POSEE]->(s)
                        """,
                        usuario_id=usuario_id,
                        skill_id=skill_id
                    )

        return usuario_dto
