from Services.DatabaseConfig import DatabaseConfig
from Services.HistorialService import HistorialService
from Services.UsuarioServices import UsuarioService
from bson import ObjectId, errors
from datetime import datetime
db_config = DatabaseConfig()
neo4j = db_config.get_neo4j_driver()

db = DatabaseConfig().get_mongo_db()
equipo_collection = db["equipos"]
usuario_collection = db["usuarios"]

class EquipoService:

    @staticmethod
    def _validar_usuarios_existentes(usuario_ids: list[str]):
        existentes = usuario_collection.find({"_id": {"$in": [ObjectId(uid) for uid in usuario_ids]}})
        existentes_ids = {str(u["_id"]) for u in existentes}
        faltantes = [uid for uid in usuario_ids if uid not in existentes_ids]
        if faltantes:
            raise ValueError(f"Usuarios no válidos o inexistentes: {faltantes}")

    @staticmethod
    def crear(data):
        EquipoService._validar_usuarios_existentes(data.get("integrantes", []))

        result = equipo_collection.insert_one(data)
        equipo_id = str(result.inserted_id)

        # Registrar en Neo4j
        try:
            with db_config.get_neo4j_driver().session() as session:
                # Crear nodo Equipo
                session.run(
                    """
                    CREATE (e:Equipo {id: $id, nombre: $nombre})
                    """,
                    id=equipo_id,
                    nombre=data.get("nombre", "")
                )

                # Crear relaciones con integrantes
                for uid in data.get("integrantes", []):
                    session.run(
                        """
                        MATCH (u:Usuario {id: $usuario_id}), (e:Equipo {id: $equipo_id})
                        MERGE (u)-[:PERTENECE_A]->(e)
                        """,
                        usuario_id=uid,
                        equipo_id=equipo_id
                    )
        except Exception as e:
            print(f"⚠️ Error registrando en Neo4j: {e}")

        # Registrar historial
        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Equipo creado",
            "fecha": datetime.now()
        })

        return {**data, "id": equipo_id}

    @staticmethod
    def eliminar_integrante(equipo_id: str, usuario_id: str):
        equipo = equipo_collection.find_one({"_id": ObjectId(equipo_id)})
        if not equipo:
            raise ValueError("Equipo no encontrado")

        if usuario_id not in equipo.get("integrantes", []):
            raise ValueError("Este usuario no pertenece al equipo")

        nuevos_integrantes = [uid for uid in equipo["integrantes"] if uid != usuario_id]
        exs = equipo.get("ex_integrantes", [])
        if usuario_id not in exs:
            exs.append(usuario_id)

        equipo_collection.update_one(
            {"_id": ObjectId(equipo_id)},
            {"$set": {
                "integrantes": nuevos_integrantes,
                "ex_integrantes": exs
            }}
        )

        # Neo4j: Eliminar relación
        try:
            with neo4j.session() as session:
                session.run(
                    """
                    MATCH (u:Usuario {id: $usuario_id})-[r:PERTENECE_A]->(e:Equipo {id: $equipo_id})
                    DELETE r
                    """,
                    usuario_id=usuario_id,
                    equipo_id=equipo_id
                )
        except Exception as e:
            print(f"⚠️ Error en Neo4j al eliminar integrante: {e}")

        HistorialService.registrar({
            "usuario_id": usuario_id,
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Usuario removido del equipo y pasado a ex-integrantes",
            "fecha": datetime.now()
        })

    @staticmethod
    def listar():
        return [
            {
                "id": str(e["_id"]),
                "nombre": e["nombre"],
                "empresa_id": e.get("empresa_id"),  # Usamos get por seguridad
                "integrantes": e.get("integrantes", []),
                "ex_integrantes": e.get("ex_integrantes", [])
            }
            for e in equipo_collection.find()
        ]

    @staticmethod
    def obtener_por_id(equipo_id: str):
        try:
            obj_id = ObjectId(equipo_id)
        except errors.InvalidId:
            raise ValueError("ID inválido o equipo inexistente")

        equipo = equipo_collection.find_one({"_id": obj_id})
        if not equipo:
            return None

        return {
            "id": str(equipo["_id"]),
            "nombre": equipo["nombre"],
            "empresa_id": equipo.get("empresa_id"),
            "integrantes": equipo.get("integrantes", []),
            "ex_integrantes": equipo.get("ex_integrantes", [])
        }

    @staticmethod
    def agregar_integrante(equipo_id: str, usuario_id: str):
        try:
            equipo_oid = ObjectId(equipo_id)
            usuario_oid = ObjectId(usuario_id)
        except errors.InvalidId:
            raise ValueError("ID inválido")

        if not UsuarioService.obtener_por_id(usuario_id):
            raise ValueError("El usuario no existe")

        equipo = equipo_collection.find_one({"_id": equipo_oid})
        if not equipo:
            raise ValueError("El equipo no existe")

        equipo.setdefault("integrantes", [])
        equipo.setdefault("ex_integrantes", [])

        if usuario_id in equipo["integrantes"]:
            raise ValueError("El usuario ya es integrante del equipo")

        if usuario_id in equipo["ex_integrantes"]:
            equipo["ex_integrantes"].remove(usuario_id)

        equipo["integrantes"].append(usuario_id)

        equipo_collection.update_one({"_id": equipo_oid}, {"$set": {
            "integrantes": equipo["integrantes"],
            "ex_integrantes": equipo["ex_integrantes"]
        }})

        # Neo4j: Crear relación
        try:
            with neo4j.session() as session:
                session.run(
                    """
                    MATCH (u:Usuario {id: $usuario_id}), (e:Equipo {id: $equipo_id})
                    MERGE (u)-[:PERTENECE_A]->(e)
                    """,
                    usuario_id=usuario_id,
                    equipo_id=equipo_id
                )
        except Exception as e:
            print(f"⚠️ Error en Neo4j al agregar integrante: {e}")

        HistorialService.registrar({
            "usuario_id": usuario_id,
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Usuario agregado al equipo",
            "fecha": datetime.now()
        })

        return EquipoService.obtener_por_id(equipo_id)


    @staticmethod
    def actualizar(equipo_id: str, update_data: dict):
        try:
            obj_id = ObjectId(equipo_id)
        except errors.InvalidId:
            raise ValueError("ID inválido")

        equipo = equipo_collection.find_one({"_id": obj_id})
        if not equipo:
            raise ValueError("Equipo no encontrado")

        # Solo permitimos actualizar algunos campos directamente
        campos_permitidos = {"nombre", "empresa_id"}
        datos_filtrados = {k: v for k, v in update_data.items() if k in campos_permitidos}

        if not datos_filtrados:
            raise ValueError("No hay campos válidos para actualizar")

        equipo_collection.update_one({"_id": obj_id}, {"$set": datos_filtrados})

        return EquipoService.obtener_por_id(equipo_id)
    
    @staticmethod
    def eliminar(equipo_id: str):
        try:
            obj_id = ObjectId(equipo_id)
        except errors.InvalidId:
            raise ValueError("ID inválido")

        equipo = equipo_collection.find_one({"_id": obj_id})
        if not equipo:
            raise ValueError("Equipo no encontrado")

        equipo_collection.delete_one({"_id": obj_id})

        HistorialService.registrar({
            "usuario_id": equipo.get("usuario_id", "sistema"),
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Equipo eliminado",
            "fecha": datetime.now()
        })

        return {"mensaje": "Equipo eliminado correctamente"}

