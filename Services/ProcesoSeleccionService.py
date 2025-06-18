from Services.DatabaseConfig import DatabaseConfig
from bson import ObjectId, errors
from datetime import datetime

db_config = DatabaseConfig()
mongo = db_config.get_mongo_db()
neo4j = db_config.get_neo4j_driver()

procesos_collection = mongo["procesos_seleccion"]
empresas = mongo["empresas"]
ofertas = mongo["ofertas"]
usuarios = mongo["usuarios"]

class ProcesoSeleccionService:

    @staticmethod
    def _validar_referencias(data):
        # Validar existencia de las entidades referenciadas
        ids = {
            "oferta_id": data.get("oferta_id"),
            "candidato_id": data.get("candidato_id"),
            "reclutador_id": data.get("reclutador_id")
        }

        for key, val in ids.items():
            if not val:
                raise ValueError(f"Falta el campo {key}")

        try:
            refs = {
                "oferta": ofertas.find_one({"_id": ObjectId(ids["oferta_id"])}),
                "candidato": usuarios.find_one({"_id": ObjectId(ids["candidato_id"])}),
                "reclutador": usuarios.find_one({"_id": ObjectId(ids["reclutador_id"])})
            }
        except Exception:
            raise ValueError("Alguno de los ID tiene un formato inválido")

        for k, v in refs.items():
            if not v:
                raise ValueError(f"{k.capitalize()} no encontrado")

    @staticmethod
    def crear(data):
        try:
            ProcesoSeleccionService._validar_referencias(data)

            data["historial"] = data.get("historial", [])
            result = procesos_collection.insert_one(data)
            proceso_id = str(result.inserted_id)

            # Neo4j
            try:
                with neo4j.session() as session:
                    session.run("""
                        CREATE (p:ProcesoSeleccion {
                            id: $id,
                            estado: $estado
                        })
                    """, id=proceso_id, estado=data.get("estado", "Pendiente"))

                    # Relaciones
                    session.run("""
                        MATCH (e:Empresa {id: $empresa_id}), (p:ProcesoSeleccion {id: $pid})
                        MERGE (e)-[:PARTICIPA_EN]->(p)
                    """, empresa_id=data["empresa_id"], pid=proceso_id)

                    session.run("""
                        MATCH (o:Oferta {id: $oferta_id}), (p:ProcesoSeleccion {id: $pid})
                        MERGE (o)-[:SELECCIONA_PARA]->(p)
                    """, oferta_id=data["oferta_id"], pid=proceso_id)

                    session.run("""
                        MATCH (u:Usuario {id: $uid}), (p:ProcesoSeleccion {id: $pid})
                        MERGE (u)-[:CANDIDATO_DE]->(p)
                    """, uid=data["candidato_id"], pid=proceso_id)

                    session.run("""
                        MATCH (u:Usuario {id: $uid}), (p:ProcesoSeleccion {id: $pid})
                        MERGE (u)-[:RECLUTADOR_DE]->(p)
                    """, uid=data["reclutador_id"], pid=proceso_id)

            except Exception as e:
                print(f"Error en Neo4j al crear proceso: {e}")

            return {**data, "id": proceso_id}
        except Exception as e:
            raise ValueError(f"Error al crear proceso: {e}")

    @staticmethod
    def listar():
        return [
            {**p, "id": str(p["_id"])}
            for p in procesos_collection.find()
        ]

    @staticmethod
    def obtener_por_id(proceso_id):
        try:
            obj_id = ObjectId(proceso_id)
            proceso = procesos_collection.find_one({"_id": obj_id})
            if not proceso:
                return None
            return {**proceso, "id": str(proceso["_id"])}
        except Exception:
            raise ValueError("ID inválido")

    @staticmethod
    def actualizar(proceso_id, data):
        try:
            obj_id = ObjectId(proceso_id)

            # Validar relaciones si alguna cambió
            if any(k in data for k in ["empresa_id", "oferta_id", "candidato_id", "reclutador_id"]):
                ProcesoSeleccionService._validar_referencias(data)

            # Obtener versión anterior para comparar
            proceso_anterior = procesos_collection.find_one({"_id": obj_id})
            if not proceso_anterior:
                raise ValueError("Proceso no encontrado")

            # Actualizar en MongoDB
            procesos_collection.update_one({"_id": obj_id}, {"$set": data})

            # Sincronizar con Neo4j
            try:
                with neo4j.session() as session:
                    # Actualizar propiedades básicas (ej: estado)
                    props = {}
                    if "estado" in data:
                        props["estado"] = data["estado"]
                        session.run("""
                            MATCH (p:ProcesoSeleccion {id: $id})
                            SET p.estado = $estado
                        """, id=proceso_id, estado=data["estado"])

                    # Relaciones posibles
                    relaciones = [
                        ("empresa_id", "Empresa", "PARTICIPA_EN"),
                        ("oferta_id", "Oferta", "SELECCIONA_PARA"),
                        ("candidato_id", "Usuario", "CANDIDATO_DE"),
                        ("reclutador_id", "Usuario", "RECLUTADOR_DE")
                    ]

                    for campo, tipo_nodo, relacion in relaciones:
                        nuevo_id = data.get(campo)
                        anterior_id = proceso_anterior.get(campo)

                        if nuevo_id and nuevo_id != anterior_id:
                            session.run(f"""
                                MATCH (p:ProcesoSeleccion {{id: $pid}})
                                OPTIONAL MATCH (n:{tipo_nodo})-[r:{relacion}]->(p)
                                DELETE r
                                WITH p
                                MATCH (nuevo:{tipo_nodo} {{id: $nuevo_id}})
                                MERGE (nuevo)-[:{relacion}]->(p)
                            """, pid=proceso_id, nuevo_id=nuevo_id)

            except Exception as e:
                print(f"Error sincronizando con Neo4j: {e}")

            return ProcesoSeleccionService.obtener_por_id(proceso_id)

        except Exception as e:
            raise ValueError(f"Error al actualizar proceso: {e}")

    @staticmethod
    def eliminar(proceso_id):
        try:
            obj_id = ObjectId(proceso_id)
            proceso = procesos_collection.find_one({"_id": obj_id})
            if not proceso:
                raise ValueError("Proceso no encontrado")

            procesos_collection.delete_one({"_id": obj_id})

            try:
                with neo4j.session() as session:
                    session.run("""
                        MATCH (p:ProcesoSeleccion {id: $id})
                        DETACH DELETE p
                    """, id=proceso_id)
            except Exception as e:
                print(f"Error al eliminar proceso en Neo4j: {e}")

            return {"mensaje": "Proceso eliminado correctamente"}
        except Exception as e:
            raise ValueError(f"Error al eliminar proceso: {e}")
