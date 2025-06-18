from Services.DatabaseConfig import DatabaseConfig
from Services.UsuarioServices import UsuarioService
from bson import ObjectId, errors
from datetime import datetime
from Dtos.Historial import Historial
from Services.EmpresaService import EmpresaService

db_config = DatabaseConfig()
neo4j = db_config.get_neo4j_driver()

db = db_config.get_mongo_db()
equipo_collection = db["equipos"]
usuario_collection = db["usuarios"]
empresa_collection = db["empresas"]

class EquipoService:
    @staticmethod
    def mongo_to_model(usuario):
        usuario["id"] = str(usuario["_id"])
        usuario.pop("_id", None)
        return usuario
    
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
        historial = data.get("historial", [])
        hoy = datetime.today()
        historial.append(Historial(fecha=hoy, mensage="Equipo creado").model_dump())
        data["historial"] = historial

        EquipoService._validar_usuarios_existentes(data.get("integrantes", []))
        result = equipo_collection.insert_one(data)
        data["id"] = str(result.inserted_id)

        empresa_id = data.get("empresa_id")
        if empresa_id:
            empresa = empresa_collection.find_one({"_id": ObjectId(empresa_id)})
            if "equipos" not in empresa or not isinstance(empresa["equipos"], list):
                empresa_collection.update_one(
                    {"_id": ObjectId(empresa_id)},
                    {"$set": {"equipos": []}}
                )
            historial_emp = empresa.get("historial", [])
            hoy = datetime.today()
            mensaje = f"El equipo '{empresa_id}' fue agregado a la empresa."
            historial_emp.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
            empresa_collection.update_one(
                {"_id": ObjectId(empresa_id)},
                {
                    "$addToSet": {"equipos": data["id"]},
                    "$set": {"historial": historial_emp}
                }
            )

        with neo4j.session() as session:
            session.run(
                "CREATE (e:Equipo {id: $id, nombre: $nombre})",
                id=data["id"],
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
                    equipo_id=data["id"]
                )

            # Relación con empresa
            if empresa_id:
                session.run(
                    """
                    MATCH (emp:Empresa {id: $empresa_id}), (e:Equipo {id: $equipo_id})
                    MERGE (emp)-[:TIENE_EQUIPO]->(e)
                    """,
                    empresa_id=empresa_id,
                    equipo_id=data["id"]
                )

        return data


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

        with neo4j.session() as session:
            session.run(
                """
                MATCH (u:Usuario {id: $usuario_id})-[r:PERTENECE_A]->(e:Equipo {id: $equipo_id})
                DELETE r
                """,
                usuario_id=usuario_id,
                equipo_id=equipo_id
            )

    @staticmethod
    def listar():
        usuarios = list(equipo_collection.find())
        return [EquipoService.mongo_to_model(u) for u in usuarios]

    @staticmethod
    def obtener_por_id(equipo_id: str):
        equipo = equipo_collection.find_one({"_id": ObjectId(equipo_id)})
        if not equipo:
            return None
        return EquipoService.mongo_to_model(equipo)


    @staticmethod
    def agregar_integrante(equipo_id: str, usuario_id: str):
        if not UsuarioService.obtener_por_id(usuario_id):
            raise ValueError("El usuario no existe")

        equipo = equipo_collection.find_one({"_id": equipo_id})
        if not equipo:
            raise ValueError("El equipo no existe")

        equipo.setdefault("integrantes", [])
        equipo.setdefault("ex_integrantes", [])

        if usuario_id in equipo["integrantes"]:
            raise ValueError("El usuario ya es integrante del equipo")

        if usuario_id in equipo["ex_integrantes"]:
            equipo["ex_integrantes"].remove(usuario_id)

        equipo["integrantes"].append(usuario_id)

        equipo_collection.update_one({"_id": equipo_id}, {"$set": {
            "integrantes": equipo["integrantes"],
            "ex_integrantes": equipo["ex_integrantes"]
        }})

        with neo4j.session() as session:
            session.run(
                """
                MATCH (u:Usuario {id: $usuario_id}), (e:Equipo {id: $equipo_id})
                MERGE (u)-[:PERTENECE_A]->(e)
                """,
                usuario_id=usuario_id,
                equipo_id=equipo_id
            )

    @staticmethod
    def actualizar(equipo_id: str, update_data: dict):
        equipo = equipo_collection.find_one({"_id": ObjectId(equipo_id)})
        if not equipo:
            raise ValueError("Equipo no encontrado")
        
        historial = equipo.get("historial", [])
        hoy = datetime.today()
        for campo, nuevo_valor in update_data.items():
            valor_anterior = equipo.get(campo, None)
            if valor_anterior == nuevo_valor:
                continue
            mensaje = f"Se cambió '{campo}' de '{valor_anterior}' a '{nuevo_valor}'"
            historial.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
        update_data["historial"] = historial

        nueva_empresa_id = update_data.get("empresa_id")
        empresa_anterior_id = equipo.get("empresa_id")

        equipo_collection.update_one({"_id": equipo_id}, {"$set": update_data})

        if nueva_empresa_id and nueva_empresa_id != empresa_anterior_id:
            empresa_anterior = empresa_collection.find_one({"_id": ObjectId(empresa_anterior_id)}) if empresa_anterior_id else None
            empresa_nueva = empresa_collection.find_one({"_id": ObjectId(nueva_empresa_id)})

            if empresa_anterior:
                if "equipos" not in empresa_anterior or not isinstance(empresa_anterior["equipos"], list):
                    empresa_collection.update_one(
                        {"_id": ObjectId(nueva_empresa_id)},
                        {"$set": {"equipos": []}}
                    )
                historial_emp = empresa_anterior.get("historial", [])
                hoy = datetime.today()
                mensaje = f"El equipo '{equipo_id}' fue removido de la empresa."
                historial_emp.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
                empresa_collection.update_one(
                    {"_id": ObjectId(empresa_anterior_id)},
                    {
                        "$pull": {"equipos": equipo_id},
                        "$set": {"historial": historial_emp}
                    }
                )

            if empresa_nueva:
                historial_emp = empresa_nueva.get("historial", [])
                hoy = datetime.today()
                mensaje = f"El equipo '{equipo_id}' fue agregado a la empresa."
                historial_emp.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
                if "equipos" not in empresa_nueva or not isinstance(empresa_nueva["equipos"], list):
                    empresa_collection.update_one(
                        {"_id": ObjectId(nueva_empresa_id)},
                        {"$set": {"equipos": []}}
                    )
                empresa_collection.update_one(
                    {"_id": ObjectId(nueva_empresa_id)},
                    {
                        "$addToSet": {"equipos": equipo_id},
                        "$set": {"historial": historial_emp}
                    }
                )

            with neo4j.session() as session:
                if empresa_anterior_id and empresa_anterior_id != nueva_empresa_id:
                    session.run(
                        """
                        MATCH (emp:Empresa {id: $empresa_id})-[r:TIENE_EQUIPO]->(e:Equipo {id: $equipo_id})
                        DELETE r
                        """,
                        empresa_id=empresa_anterior_id,
                        equipo_id=equipo_id
                    )

                if nueva_empresa_id and nueva_empresa_id != empresa_anterior_id:
                    session.run(
                        """
                        MATCH (emp:Empresa {id: $empresa_id}), (e:Equipo {id: $equipo_id})
                        MERGE (emp)-[:TIENE_EQUIPO]->(e)
                        """,
                        empresa_id=nueva_empresa_id,
                        equipo_id=equipo_id
                    )

        return EquipoService.mongo_to_model(equipo)

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


