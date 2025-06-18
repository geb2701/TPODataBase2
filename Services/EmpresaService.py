from Dtos.Historial import Historial
from Services.DatabaseConfig import DatabaseConfig
from bson import ObjectId, errors
from datetime import datetime
from fastapi import HTTPException

db_config = DatabaseConfig()
empresa_collection = db_config.get_mongo_db()["empresas"]
neo4j = db_config.get_neo4j_driver()

def mongo_to_model(item):
    item["id"] = str(item["_id"])
    item.pop("_id", None)
    return item

class EmpresaService:
    @staticmethod
    def crear(data):
        try:
            historial = data.get("historial", [])
            hoy = datetime.today()
            historial.append(Historial(fecha=hoy, mensage="Empresa creada").model_dump())
            data["historial"] = historial

            result = empresa_collection.insert_one(data)
            empresa_id = str(result.inserted_id)
            data["id"] = empresa_id

            with neo4j.session() as session:
                session.run(
                    "CREATE (e:Empresa {id: $id, nombre: $nombre})",
                    id=empresa_id,
                    nombre=data.get("nombre", "")
                )

            return data
        except Exception as e:
            raise ValueError(f"Error al crear empresa: {e}")

    @staticmethod
    def listar():
        try:
            return [mongo_to_model(e) for e in empresa_collection.find()]
        except Exception as e:
            raise ValueError(f"Error al listar empresas: {e}")

    @staticmethod
    def obtener_por_id(empresa_id: str):
        try:
            obj_id = ObjectId(empresa_id)
            empresa = empresa_collection.find_one({"_id": obj_id})
            if not empresa:
                return None
            return mongo_to_model(empresa)
        except errors.InvalidId:
            raise ValueError("ID de empresa inválido")
        except Exception as e:
            raise ValueError(f"Error al obtener empresa: {e}")

    @staticmethod
    def actualizar(empresa_id: str, data):
        try:
            usuario = empresa_collection.find_one({"_id": ObjectId(empresa_id)})
            if not usuario:
                return None

            historial = usuario.get("historial", [])
            hoy = datetime.today()
            for campo, nuevo_valor in data.items():
                valor_anterior = usuario.get(campo, None)
                if valor_anterior == nuevo_valor:
                    continue
                mensaje = f"Se cambió '{campo}' de '{valor_anterior}' a '{nuevo_valor}'"
                historial.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
            data["historial"] = historial

            result = empresa_collection.update_one(
                {"_id": ObjectId(empresa_id)},
                {"$set": data}
            )
            result = mongo_to_model(usuario)
            
            with neo4j.session() as session:
                session.run(
                    """
                    MATCH (e:Empresa {id: $empresa_id})
                    SET e.nombre = $nuevo_nombre
                    """,
                    empresa_id=empresa_id,
                    nuevo_nombre=data["nombre"]
                )

            return result
        except errors.InvalidId:
            raise ValueError("ID de empresa inválido")
        except Exception as e:
            raise ValueError(f"Error al actualizar empresa: {e}")

    @staticmethod
    def eliminar(empresa_id: str):
        try:
            obj_id = ObjectId(empresa_id)
            result = empresa_collection.delete_one({"_id": obj_id})
            if result.deleted_count == 0:
                raise ValueError("Empresa no encontrada o ya eliminada")

            # Neo4j
            try:
                with neo4j.session() as session:
                    session.run(
                        "MATCH (e:Empresa {id: $id}) DETACH DELETE e",
                        id=empresa_id
                    )
            except Exception as e:
                print(f"⚠️ Error al eliminar empresa en Neo4j: {e}")
        except errors.InvalidId:
            raise ValueError("ID de empresa inválido")
        except Exception as e:
            raise ValueError(f"Error al eliminar empresa: {e}")
