from Services.DatabaseConfig import DatabaseConfig
from Services.HistorialService import HistorialService
from bson import ObjectId
from datetime import datetime

db_config = DatabaseConfig()
empresa_collection = db_config.get_mongo_db()["empresas"]

class EmpresaService:

    @staticmethod
    def crear(data):
        result = empresa_collection.insert_one(data)
        empresa_id = str(result.inserted_id)

        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": empresa_id,
            "tipo": "empresa",
            "cambio": "Empresa creada",
            "fecha": datetime.now()
        })

        return {**data, "id": empresa_id}

    @staticmethod
    def listar():
        return [{**e, "id": str(e["_id"])} for e in empresa_collection.find()]

    @staticmethod
    def obtener_por_id(empresa_id: str):
        empresa = empresa_collection.find_one({"_id": ObjectId(empresa_id)})
        if not empresa:
            return None
        return {**empresa, "id": str(empresa["_id"])}

    @staticmethod
    def actualizar(empresa_id: str, data):
        empresa_collection.update_one({"_id": ObjectId(empresa_id)}, {"$set": data})

        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": empresa_id,
            "tipo": "empresa",
            "cambio": "Empresa actualizada",
            "fecha": datetime.now()
        })

        return EmpresaService.obtener_por_id(empresa_id)

    @staticmethod
    def eliminar(empresa_id: str):
        empresa_collection.delete_one({"_id": ObjectId(empresa_id)})

        HistorialService.registrar({
            "usuario_id": "sistema",
            "entidad_id": empresa_id,
            "tipo": "empresa",
            "cambio": "Empresa eliminada",
            "fecha": datetime.now()
        })
