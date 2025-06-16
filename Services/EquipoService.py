from Services.DatabaseConfig import DatabaseConfig
from Services.UsuarioServices import UsuarioService
from bson import ObjectId, errors
from datetime import datetime

db_config = DatabaseConfig()
neo4j = db_config.get_neo4j_driver()

db = db_config.get_mongo_db()
equipo_collection = db["equipos"]
usuario_collection = db["usuarios"]

class EquipoService:

    @staticmethod
    def _validar_usuarios_existentes(usuario_ids: list[str]):
        try:
            obj_ids = [ObjectId(uid) for uid in usuario_ids]
        except Exception:
            raise ValueError("Formato de ID inválido en la lista de usuarios")

        existentes = usuario_collection.find({"_id": {"$in": obj_ids}})
        existentes_ids = {str(u["_id"]) for u in existentes}
        faltantes = [uid for uid in usuario_ids if uid not in existentes_ids]

        if faltantes:
            raise ValueError(f"Usuarios no válidos o inexistentes: {faltantes}")

    @staticmethod
    def crear(data):
        try:
            EquipoService._validar_usuarios_existentes(data.get("integrantes", []))
            result = equipo_collection.insert_one(data)
            equipo_id = str(result.inserted_id)

            # 🟢 MongoDB: Agregar ID de equipo a la empresa (si corresponde)
            empresa_id = data.get("empresa_id")
            if empresa_id:
                try:
                    empresa_collection = db["empresas"]
                    empresa_collection.update_one(
                        {"_id": ObjectId(empresa_id)},
                        {"$addToSet": {"equipos": equipo_id}}  # evita duplicados
                    )
                except Exception as e:
                    print(f"⚠️ Error actualizando empresa en MongoDB: {e}")

            # 🔵 Neo4j
            try:
                with neo4j.session() as session:
                    # Crear nodo Equipo
                    session.run(
                        "CREATE (e:Equipo {id: $id, nombre: $nombre})",
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

                    # Relación con empresa
                    if empresa_id:
                        session.run(
                            """
                            MATCH (emp:Empresa {id: $empresa_id}), (e:Equipo {id: $equipo_id})
                            MERGE (emp)-[:TIENE_EQUIPO]->(e)
                            """,
                            empresa_id=empresa_id,
                            equipo_id=equipo_id
                        )
            except Exception as e:
                print(f"⚠️ Error en Neo4j (crear equipo): {e}")

            return {**data, "id": equipo_id}
        except Exception as e:
            raise ValueError(f"Error al crear equipo: {e}")


    @staticmethod
    def eliminar_integrante(equipo_id: str, usuario_id: str):
        try:
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
        except Exception as e:
            raise ValueError(f"Error al remover integrante: {e}")

    @staticmethod
    def listar():
        return [
            {
                "id": str(e["_id"]),
                "nombre": e["nombre"],
                "empresa_id": e.get("empresa_id"),
                "integrantes": e.get("integrantes", []),
                "ex_integrantes": e.get("ex_integrantes", [])
            }
            for e in equipo_collection.find()
        ]

    @staticmethod
    def obtener_por_id(equipo_id: str):
        try:
            obj_id = ObjectId(equipo_id)
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
        except Exception:
            raise ValueError("ID inválido o equipo no encontrado")

    @staticmethod
    def agregar_integrante(equipo_id: str, usuario_id: str):
        try:
            equipo_oid = ObjectId(equipo_id)
            usuario_oid = ObjectId(usuario_id)
        except Exception:
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

        return EquipoService.obtener_por_id(equipo_id)

    @staticmethod
    def actualizar(equipo_id: str, update_data: dict):
        try:
            obj_id = ObjectId(equipo_id)
            equipo = equipo_collection.find_one({"_id": obj_id})
            if not equipo:
                raise ValueError("Equipo no encontrado")

            campos_permitidos = {"nombre", "empresa_id"}
            datos_filtrados = {k: v for k, v in update_data.items() if k in campos_permitidos}

            if not datos_filtrados:
                raise ValueError("No hay campos válidos para actualizar")

            # Detectar si se cambió la empresa
            nueva_empresa_id = datos_filtrados.get("empresa_id")
            empresa_anterior_id = equipo.get("empresa_id")

            # Actualización en MongoDB
            equipo_collection.update_one({"_id": obj_id}, {"$set": datos_filtrados})

            empresa_collection = db["empresas"]

            if nueva_empresa_id and nueva_empresa_id != empresa_anterior_id:
                # 🔄 Quitar equipo de la empresa anterior
                if empresa_anterior_id:
                    try:
                        empresa_collection.update_one(
                            {"_id": ObjectId(empresa_anterior_id)},
                            {"$pull": {"equipos": equipo_id}}
                        )
                    except Exception as e:
                        print(f"⚠️ Error quitando equipo de empresa anterior: {e}")

                # ➕ Agregar equipo a la nueva empresa
                try:
                    empresa_collection.update_one(
                        {"_id": ObjectId(nueva_empresa_id)},
                        {"$addToSet": {"equipos": equipo_id}}
                    )
                except Exception as e:
                    print(f"⚠️ Error agregando equipo a empresa nueva: {e}")

            # Neo4j: actualizar relación empresa-equipo
            try:
                with neo4j.session() as session:
                    # Eliminar relación vieja
                    if empresa_anterior_id and empresa_anterior_id != nueva_empresa_id:
                        session.run(
                            """
                            MATCH (emp:Empresa {id: $empresa_id})-[r:TIENE_EQUIPO]->(e:Equipo {id: $equipo_id})
                            DELETE r
                            """,
                            empresa_id=empresa_anterior_id,
                            equipo_id=equipo_id
                        )
                    # Crear relación nueva
                    if nueva_empresa_id and nueva_empresa_id != empresa_anterior_id:
                        session.run(
                            """
                            MATCH (emp:Empresa {id: $empresa_id}), (e:Equipo {id: $equipo_id})
                            MERGE (emp)-[:TIENE_EQUIPO]->(e)
                            """,
                            empresa_id=nueva_empresa_id,
                            equipo_id=equipo_id
                        )
            except Exception as e:
                print(f"⚠️ Error en Neo4j al actualizar empresa del equipo: {e}")

            return EquipoService.obtener_por_id(equipo_id)
        except Exception as e:
            raise ValueError(f"Error al actualizar equipo: {e}")

    @staticmethod
    def eliminar(equipo_id: str):
        try:
            # Validación del formato del ID
            try:
                obj_id = ObjectId(equipo_id)
            except Exception:
                raise ValueError("ID de equipo inválido")

            # Verificamos si el equipo existe en MongoDB
            equipo = equipo_collection.find_one({"_id": obj_id})
            if not equipo:
                raise ValueError("El equipo ya fue eliminado o no existe")

            empresa_id = equipo.get("empresa_id")
            empresa_collection = db["empresas"]

            # 🔄 Si tiene empresa, quitar referencia
            if empresa_id:
                try:
                    empresa_collection.update_one(
                        {"_id": ObjectId(empresa_id)},
                        {"$pull": {"equipos": equipo_id}}
                    )
                except Exception as e:
                    print(f"⚠️ Error al quitar equipo de empresa en MongoDB: {e}")

            # Eliminación en MongoDB
            equipo_collection.delete_one({"_id": obj_id})

            # 🧠 Eliminación en Neo4j
            try:
                with neo4j.session() as session:
                    # Eliminar nodo equipo
                    session.run(
                        """
                        MATCH (e:Equipo {id: $equipo_id})
                        DETACH DELETE e
                        """,
                        equipo_id=equipo_id
                    )
                    # Eliminar relación con empresa, si existía
                    if empresa_id:
                        session.run(
                            """
                            MATCH (emp:Empresa {id: $empresa_id})-[r:TIENE_EQUIPO]->(e:Equipo {id: $equipo_id})
                            DELETE r
                            """,
                            empresa_id=empresa_id,
                            equipo_id=equipo_id
                        )
            except Exception as e:
                print(f"⚠️ Error al eliminar en Neo4j: {e}")

            return {"mensaje": "Equipo eliminado correctamente"}
        except Exception as e:
            raise ValueError(f"Error al eliminar equipo: {e}")


