from Services.DatabaseConfig import DatabaseConfig
from Services.HistorialService import HistorialService
from bson import ObjectId
from datetime import datetime

db = DatabaseConfig().get_mongo_db()
oferta_collection = db["ofertas"]

class OfertaService:

    @staticmethod
    def crear(data):
        result = oferta_collection.insert_one(data)
        oferta_id = str(result.inserted_id)

        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": oferta_id,
            "tipo": "oferta",
            "cambio": "Oferta creada",
            "fecha": datetime.now()
        })

        return {**data, "id": oferta_id}

    @staticmethod
    def listar():
        return [{**o, "id": str(o["_id"])} for o in oferta_collection.find()]

    @staticmethod
    def obtener_por_id(oferta_id: str):
        oferta = oferta_collection.find_one({"_id": ObjectId(oferta_id)})
        if not oferta:
            return None
        return {**oferta, "id": str(oferta["_id"])}

    @staticmethod
    def actualizar(oferta_id: str, data):
        oferta_collection.update_one({"_id": ObjectId(oferta_id)}, {"$set": data})

        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": oferta_id,
            "tipo": "oferta",
            "cambio": "Oferta actualizada",
            "fecha": datetime.now()
        })

        return OfertaService.obtener_por_id(oferta_id)

    @staticmethod
    def eliminar(oferta_id: str):
        oferta_collection.delete_one({"_id": ObjectId(oferta_id)})

        HistorialService.registrar({
            "usuario_id": "sistema",
            "entidad_id": oferta_id,
            "tipo": "oferta",
            "cambio": "Oferta eliminada",
            "fecha": datetime.now()
        })
    
    @staticmethod
    def buscar_por_empresa(empresa_id: str):
        return [
            {**o, "id": str(o["_id"])}
            for o in oferta_collection.find({"empresa_id": empresa_id})
        ]

    @staticmethod
    def buscar_activas():
        return [
            {**o, "id": str(o["_id"])}
            for o in oferta_collection.find({"estado": "Activa"})
        ]

