from Services.DatabaseConfig import DatabaseConfig
from bson import ObjectId

db_config = DatabaseConfig()
mongo = db_config.get_mongo_db()
equipos_collection = mongo["equipos"]

class EquipoService:

    @staticmethod
    def crear_equipo(data):
        result = equipos_collection.insert_one(data)
        return {**data, "id": str(result.inserted_id)}

    @staticmethod
    def listar_equipos():
        return [{**e, "id": str(e["_id"])} for e in equipos_collection.find()]

    @staticmethod
    def obtener_equipo_por_id(equipo_id):
        equipo = equipos_collection.find_one({"_id": ObjectId(equipo_id)})
        if not equipo:
            return None
        return {**equipo, "id": str(equipo["_id"])}

    @staticmethod
    def actualizar_equipo(equipo_id, data):
        equipos_collection.update_one({"_id": ObjectId(equipo_id)}, {"$set": data})
        return EquipoService.obtener_equipo_por_id(equipo_id)

    @staticmethod
    def eliminar_equipo(equipo_id):
        equipos_collection.delete_one({"_id": ObjectId(equipo_id)})
