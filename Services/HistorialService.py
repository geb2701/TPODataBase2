from Services.DatabaseConfig import DatabaseConfig
from bson import ObjectId

db = DatabaseConfig().get_mongo_db()
historial_collection = db["historial"]

class HistorialService:

    @staticmethod
    def registrar(historial_item: dict):
        result = historial_collection.insert_one(historial_item)
        return {**historial_item, "id": str(result.inserted_id)}

    @staticmethod
    def buscar_por_usuario(usuario_id: str):
        return [
            {**h, "id": str(h["_id"])}
            for h in historial_collection.find({"usuario_id": usuario_id})
        ]
