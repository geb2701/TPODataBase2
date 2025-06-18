from Services.DatabaseConfig import DatabaseConfig
from bson import ObjectId, errors
from fastapi import HTTPException

db = DatabaseConfig().get_mongo_db()
neo4j = DatabaseConfig().get_neo4j_driver()
oferta_collection = db["ofertas"]
empresa_collection = db["empresas"]

class OfertaService:

    @staticmethod
    def crear(data):
        try:
            empresa_id = data.get("empresa_id")
            if not empresa_id:
                raise ValueError("Falta el campo 'empresa_id'")
            
            # Validar empresa
            empresa = empresa_collection.find_one({"_id": ObjectId(empresa_id)})
            if not empresa:
                raise ValueError("Empresa no encontrada")

            skills = data.get("skills", [])
            if not isinstance(skills, list):
                raise ValueError("El campo 'skills' debe ser una lista")

            # Validar que las skills existan en Mongo
            skills_collection = db["skills"]
            skills_validas = list(skills_collection.find({"_id": {"$in": [ObjectId(sid) for sid in skills]}}))
            if len(skills_validas) != len(skills):
                raise ValueError("Una o más skills no existen")

            # Guardar en Mongo
            result = oferta_collection.insert_one(data)
            oferta_id = str(result.inserted_id)

            # Registrar en Neo4j
            try:
                with neo4j.session() as session:
                    # Crear nodo
                    session.run("""
                        CREATE (o:Oferta {
                            id: $id,
                            titulo: $titulo,
                            descripcion: $descripcion,
                            estado: $estado
                        })
                    """, 
                    id=oferta_id,
                    titulo=data.get("titulo", ""),
                    descripcion=data.get("descripcion", ""),
                    estado=data.get("estado", "Activa"))

                    # Relación empresa -> oferta
                    session.run("""
                        MATCH (e:Empresa {id: $empresa_id}), (o:Oferta {id: $oferta_id})
                        MERGE (e)-[:PUBLICA]->(o)
                    """, empresa_id=empresa_id, oferta_id=oferta_id)

                    # Relación oferta -> skills
                    for skill_id in skills:
                        session.run("""
                            MATCH (s:Skill {id: $skill_id}), (o:Oferta {id: $oferta_id})
                            MERGE (o)-[:REQUIERE]->(s)
                        """, skill_id=skill_id, oferta_id=oferta_id)

            except Exception as e:
                print(f"Error al registrar oferta en Neo4j: {e}")

            return {**data, "id": oferta_id}
        except Exception as e:
            raise ValueError(f"Error al crear oferta: {e}")

    @staticmethod
    def listar():
        try:
            return [{**o, "id": str(o["_id"])} for o in oferta_collection.find()]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al listar ofertas: {e}")

    @staticmethod
    def obtener_por_id(oferta_id: str):
        try:
            oferta = oferta_collection.find_one({"_id": ObjectId(oferta_id)})
            if not oferta:
                return None
            return {**oferta, "id": str(oferta["_id"])}
        except Exception:
            raise ValueError("ID de oferta inválido")

    @staticmethod
    def actualizar(oferta_id: str, data):
        try:
            obj_id = ObjectId(oferta_id)
            oferta_anterior = oferta_collection.find_one({"_id": obj_id})
            if not oferta_anterior:
                raise ValueError("Oferta no encontrada")

            # Validar skills si se pasan
            skills = data.get("skills")
            if skills is not None:
                if not isinstance(skills, list):
                    raise ValueError("El campo 'skills' debe ser una lista")
                
                skills_collection = db["skills"]
                skills_validas = list(skills_collection.find({"_id": {"$in": [ObjectId(sid) for sid in skills]}}))
                if len(skills_validas) != len(skills):
                    raise ValueError("Una o más skills no existen")

            # Actualizar MongoDB
            oferta_collection.update_one({"_id": obj_id}, {"$set": data})

            # Actualizar Neo4j
            try:
                with neo4j.session() as session:
                    # 🔹 Actualizar propiedades
                    session.run("""
                        MATCH (o:Oferta {id: $id})
                        SET o += $props
                    """, id=oferta_id, props={
                        "titulo": data.get("titulo", oferta_anterior.get("titulo")),
                        "descripcion": data.get("descripcion", oferta_anterior.get("descripcion")),
                        "estado": data.get("estado", oferta_anterior.get("estado"))
                    })

                    # 🔸 Actualizar relación con empresa si cambió
                    nueva_empresa_id = data.get("empresa_id")
                    empresa_anterior_id = oferta_anterior.get("empresa_id")

                    if nueva_empresa_id and nueva_empresa_id != empresa_anterior_id:
                        session.run("""
                            MATCH (emp:Empresa)-[r:PUBLICA]->(o:Oferta {id: $oferta_id})
                            DELETE r
                        """, oferta_id=oferta_id)

                        session.run("""
                            MATCH (e:Empresa {id: $empresa_id}), (o:Oferta {id: $oferta_id})
                            MERGE (e)-[:PUBLICA]->(o)
                        """, empresa_id=nueva_empresa_id, oferta_id=oferta_id)

                    # 🔹 Actualizar skills si se enviaron
                    if skills is not None:
                        # Eliminar relaciones antiguas
                        session.run("""
                            MATCH (o:Oferta {id: $oferta_id})-[r:REQUIERE]->(:Skill)
                            DELETE r
                        """, oferta_id=oferta_id)

                        # Crear nuevas relaciones
                        for skill_id in skills:
                            session.run("""
                                MATCH (s:Skill {id: $skill_id}), (o:Oferta {id: $oferta_id})
                                MERGE (o)-[:REQUIERE]->(s)
                            """, skill_id=skill_id, oferta_id=oferta_id)
            except Exception as e:
                print(f"⚠️ Error al actualizar en Neo4j: {e}")

            return OfertaService.obtener_por_id(oferta_id)
        except Exception as e:
            raise ValueError(f"Error al actualizar oferta: {e}")

    @staticmethod
    def eliminar(oferta_id: str):
        try:
            obj_id = ObjectId(oferta_id)
            oferta = oferta_collection.find_one({"_id": obj_id})
            if not oferta:
                raise ValueError("La oferta ya fue eliminada o no existe")

            oferta_collection.delete_one({"_id": obj_id})

            try:
                with neo4j.session() as session:
                    session.run("""
                        MATCH (o:Oferta {id: $oferta_id})
                        DETACH DELETE o
                    """, oferta_id=oferta_id)
            except Exception as e:
                print(f"⚠️ Error al eliminar oferta en Neo4j: {e}")
        except Exception as e:
            raise ValueError(f"Error al eliminar oferta: {e}")

    @staticmethod
    def buscar_por_empresa(empresa_id: str):
        try:
            return [
                {**o, "id": str(o["_id"])}
                for o in oferta_collection.find({"empresa_id": empresa_id})
            ]
        except Exception as e:
            raise ValueError(f"Error al buscar ofertas por empresa: {e}")

    @staticmethod
    def buscar_activas():
        try:
            return [
                {**o, "id": str(o["_id"])}
                for o in oferta_collection.find({"estado": "Activa"})
            ]
        except Exception as e:
            raise ValueError(f"Error al buscar ofertas activas: {e}")
