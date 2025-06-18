
from datetime import datetime
from Dtos.Historial import Historial
from Services.DatabaseConfig import DatabaseConfig
from bson import ObjectId, errors
from fastapi import HTTPException

db = DatabaseConfig().get_mongo_db()
neo4j = DatabaseConfig().get_neo4j_driver()
oferta_collection = db["ofertas"]
empresa_collection = db["empresas"]
skills_collection = db["skills"]

def mongo_to_model(cert):
    cert["id"] = str(cert["_id"])
    cert.pop("_id", None)
    return cert

def validar_empresa_existe(id):
    skill = empresa_collection.find_one({"_id": ObjectId(id)})
    if not skill:
        raise HTTPException(status_code=500, detail="El ID de empresa no existe.")

def validar_skills_existen(skills_ids):
    if not skills_ids:
        return
    existentes = list(skills_collection.find({"_id": {"$in": [ObjectId(s) for s in skills_ids]}}))
    if len(existentes) != len(skills_ids):
        raise HTTPException(status_code=500, detail="Uno o más IDs de skills no existen.")

class OfertaService:
    @staticmethod
    def crear(data):
        validar_empresa_existe(data.get("empresa_id"))
        validar_skills_existen(data.get("skills", []))

        historial = data.get("historial", [])
        hoy = datetime.today()
        historial.append(Historial(fecha=hoy, mensage="Oferta creada").model_dump())
        data["historial"] = historial

        result = oferta_collection.insert_one(data)
        data["id"] = str(result.inserted_id)

        with neo4j.session() as session:
            session.run("""
                CREATE (o:Oferta {
                    id: $id,
                    puesto: $puesto,
                    categoria: $categoria,
                    modalidad: $modalidad,
                    estado: $estado
                })
            """, 
            id=data["id"],
            puesto=data.get("puesto", ""),
            categoria=data.get("categoria", ""),
            modalidad=data.get("modalidad", ""),
            estado=data.get("estado", "Activa"),)


            session.run("""
                MATCH (e:Empresa {id: $empresa_id}), (o:Oferta {id: $oferta_id})
                MERGE (e)-[:PUBLICA]->(o)
            """, empresa_id=data["empresa_id"], oferta_id=data["id"])


            for skill_id in data.get("skills", []):
                session.run("""
                    MATCH (s:Skill {id: $skill_id}), (o:Oferta {id: $oferta_id})
                    MERGE (o)-[:REQUIERE]->(s)
                """, skill_id=skill_id, oferta_id=data["id"])

        return mongo_to_model(data)


    @staticmethod
    def listar():
        oferta = list(oferta_collection.find())
        return [mongo_to_model(c) for c in oferta]
        
    @staticmethod
    def obtener_por_id(oferta_id: str):
        oferta = oferta_collection.find_one({"_id": ObjectId(oferta_id)})
        if not oferta:
            return None
        return mongo_to_model(oferta)

    @staticmethod
    def actualizar(oferta_id: str, data):
        oferta = oferta_collection.find_one({"_id": ObjectId(oferta_id)})
        if not oferta:
            raise ValueError("Oferta no encontrada")

        skills = data.get("skills")
        if skills is not None:
            validar_skills_existen(skills_ids=skills)

        historial = oferta.get("historial", [])
        hoy = datetime.today()
        for campo, nuevo_valor in data.items():
            valor_anterior = oferta.get(campo, None)
            if valor_anterior == nuevo_valor:
                continue
            mensaje = f"Se cambió '{campo}' de '{valor_anterior}' a '{nuevo_valor}'"
            historial.append(Historial(fecha=hoy, mensage=mensaje).model_dump())
        data["historial"] = historial

        oferta = oferta_collection.update_one({"_id": oferta_id}, {"$set": data})

        with neo4j.session() as session:
            session.run("""
                MATCH (o:Oferta {id: $id})
                SET o += $props
            """, id=oferta_id, props={
                "titulo": data.get("titulo", oferta.get("titulo")),
                "descripcion": data.get("descripcion", oferta.get("descripcion")),
                "estado": data.get("estado", oferta.get("estado")),
                "puesto": data.get("puesto", oferta.get("puesto")),
                "categoria": data.get("categoria", oferta.get("categoria")),
                "modalidad": data.get("modalidad", oferta.get("modalidad"))
            })

            if skills is not None:
                session.run("""
                    MATCH (o:Oferta {id: $oferta_id})-[r:REQUIERE]->(:Skill)
                    DELETE r
                """, oferta_id=oferta_id)

                for skill_id in skills:
                    session.run("""
                        MATCH (s:Skill {id: $skill_id}), (o:Oferta {id: $oferta_id})
                        MERGE (o)-[:REQUIERE]->(s)
                    """, skill_id=skill_id, oferta_id=oferta_id)


        return mongo_to_model(data)

    @staticmethod
    def buscar_por_empresa(empresa_id: str):
        ofertas = list(oferta_collection.find({"empresa_id": empresa_id}))
        return [mongo_to_model(o) for o in ofertas]

    @staticmethod
    def buscar_activas():
        ofertas = list(oferta_collection.find({"estado": "Activa"}))
        return [mongo_to_model(o) for o in ofertas]
