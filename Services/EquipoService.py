from Services.DatabaseConfig import DatabaseConfig
from Services.HistorialService import HistorialService
from bson import ObjectId
from datetime import datetime

db = DatabaseConfig().get_mongo_db()
equipo_collection = db["equipos"]

class EquipoService:

    @staticmethod
    def crear(data):
        result = equipo_collection.insert_one(data)
        equipo_id = str(result.inserted_id)

        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Equipo creado",
            "fecha": datetime.now()
        })

        return {**data, "id": equipo_id}

    @staticmethod
    def listar():
        return [{**e, "id": str(e["_id"])} for e in equipo_collection.find()]

    @staticmethod
    def obtener_por_id(equipo_id: str):
        equipo = equipo_collection.find_one({"_id": ObjectId(equipo_id)})
        if not equipo:
            return None
        return {**equipo, "id": str(equipo["_id"])}

    @staticmethod
    def actualizar(equipo_id: str, data):
        equipo_collection.update_one({"_id": ObjectId(equipo_id)}, {"$set": data})

        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Equipo actualizado",
            "fecha": datetime.now()
        })

        return EquipoService.obtener_por_id(equipo_id)

    @staticmethod
    def eliminar(equipo_id: str):
        equipo_collection.delete_one({"_id": ObjectId(equipo_id)})

        HistorialService.registrar({
            "usuario_id": "sistema",
            "entidad_id": equipo_id,
            "tipo": "equipo",
            "cambio": "Equipo eliminado",
            "fecha": datetime.now()
        })
