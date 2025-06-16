from Dtos import Historial
from Services.DatabaseConfig import DatabaseConfig
from Services.HistorialService import HistorialService
from bson import ObjectId
from datetime import datetime

db_config = DatabaseConfig()
empresa_collection = db_config.get_mongo_db()["empresas"]

def mongo_to_model(item):
    item["id"] = str(item["_id"])
    item.pop("_id", None)
    return item

class EmpresaService:
    @staticmethod
    def crear(data):
        historial = data.get("historial", [])
        hoy = datetime.today()
        historial.append(Historial(fecha=hoy, mensage="Usuario creado").model_dump())
        data["historial"] = historial

        result = empresa_collection.insert_one(data)
        data["id"] = str(result.inserted_id)

        with db_config.neo4j.session() as session:
            session.run(
                """
                CREATE (u:Empresa {id: $id, nombre: $nombre})
                """,
                id=data["id"],
                nombre=data.get("nombre", "")
            )

        return data

    @staticmethod
    def listar():
        return [mongo_to_model(e) for e in empresa_collection.find()]

    @staticmethod
    def obtener_por_id(empresa_id: str):
        empresa = empresa_collection.find_one({"_id": ObjectId(empresa_id)})
        if not empresa:
            return None
        return {**empresa, "id": str(empresa["_id"])}

    @staticmethod
    def actualizar(empresa_id: str, data):
        empresa_collection.update_one({"_id": ObjectId(empresa_id)}, {"$set": data})
        return EmpresaService.obtener_por_id(empresa_id)

    @staticmethod
    def eliminar(empresa_id: str):
        empresa_collection.delete_one({"_id": ObjectId(empresa_id)})
