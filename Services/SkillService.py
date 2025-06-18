from datetime import datetime
from bson import ObjectId
from neo4j import GraphDatabase
from Dtos.Historial import Historial
from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()
skills_collection = mongo_db["skills"]


class UsuarioService:
    @staticmethod
    def mongo_to_model(skill):
        skill["id"] = str(skill["_id"])
        skill.pop("_id", None)
        return skill

    @staticmethod
    def crear(data):
        historial = data.get("historial", [])
        hoy = datetime.today()
        historial.append(Historial(fecha=hoy, mensage="Usuario creado").model_dump())
        data["historial"] = historial

        existente = skills_collection.find_one({
            "tipo": data.get("tipo"),
            "nivel": data.get("nivel")
        })
        if existente:
            raise ValueError("Ya existe una skill con el mismo nombre y nivel.")

        result = skills_collection.insert_one(data)
        data["id"] = str(result.inserted_id)

        with neo4j.session() as session:
            session.run(
                """
                CREATE (s:Skill {id: $id, nombre: $nombre, nivel: $nivel})
                """,
                id=data["id"],
                nombre=data.get("nombre"),
                nivel=data.get("nivel"),
                
            )
        return data

    @staticmethod
    def listar():
        usuarios = list(usuarios_collection.find())
        return [UsuarioService.mongo_to_model(u) for u in usuarios]

    @staticmethod
    def obtener_por_id(usuario_id):
        usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
        if usuario:
            return UsuarioService.mongo_to_model(usuario)
        return None

    @staticmethod
    def actualizar(usuario_id, update_data):
        usuario = usuarios_collection.find_one({"_id": ObjectId(usuario_id)})
        if not usuario:
            return None

        historial = usuario.get("historial", [])
        hoy = datetime.today()
        for campo, nuevo_valor in update_data.items():
            valor_anterior = usuario.get(campo, None)
            if valor_anterior == nuevo_valor:
                continue
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
        usuario_model = UsuarioService.mongo_to_model(usuario)
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
                    
        return usuario_model
