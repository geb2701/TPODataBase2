from Dtos import Historial
from Services.DatabaseConfig import DatabaseConfig
from Services.HistorialService import HistorialService
from bson import ObjectId
from datetime import datetime

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
        # Registrar historial en Mongo
        historial = data.get("historial", [])
        hoy = datetime.today()
        historial.append(Historial(fecha=hoy, mensage="Empresa creada").model_dump())
        data["historial"] = historial

        # Insertar en MongoDB
        result = empresa_collection.insert_one(data)
        empresa_id = str(result.inserted_id)
        data["id"] = empresa_id

        # Registrar en Neo4j
        try:
            with neo4j.session() as session:
                session.run(
                    """
                    CREATE (e:Empresa {id: $id, nombre: $nombre})
                    """,
                    id=empresa_id,
                    nombre=data.get("nombre", "")
                )
        except Exception as e:
            print(f"⚠️ Error registrando empresa en Neo4j: {e}")

        # Registrar en colección de historial central si aplica
        HistorialService.registrar({
            "usuario_id": data.get("usuario_id", "sistema"),
            "entidad_id": empresa_id,
            "tipo": "empresa",
            "cambio": "Empresa creada",
            "fecha": hoy
        })

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
