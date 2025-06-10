from pymongo import MongoClient
from neo4j import GraphDatabase

# 🔌 Conexión a MongoDB Atlas
mongo = MongoClient("mongodb+srv://TPODataBase2:WcTpJOR9ZuFPxNmW@tpodatabase2.dvx531v.mongodb.net/")
db = mongo["talentum"]

# 🔌 Conexión a Neo4j local (modificá si usás Aura)
neo4j = GraphDatabase.driver("neo4j+s://bd136a15.databases.neo4j.io", auth=("neo4j", "0czpIif4DzPnO1prJ8QjyfSBHut1LKTo2ZeX-Y4rndQ"))
neo4j.verify_connectivity()


# 📥 Función para cargar candidatos y experiencia
def cargar_candidato(tx, c):
    tx.run("""
        MERGE (cand:Candidato {email: $email})
        SET cand.nombre = $nombre
    """, email=c["email"], nombre=c["nombre"])

    for skill in c.get("skills_tecnicos", []) + c.get("skills_blandos", []):
        tx.run("""
            MERGE (s:Skill {nombre: $skill})
            MERGE (cand:Candidato {email: $email})
            MERGE (cand)-[:TIENE_SKILL]->(s)
        """, skill=skill, email=c["email"])

    for exp in c.get("experiencia", []):
        tx.run("""
            MERGE (e:Empresa {nombre: $empresa})
            MERGE (cand:Candidato {email: $email})
            MERGE (cand)-[:TRABAJO_EN {rol: $rol, años: $anios}]->(e)
        """, empresa=exp["empresa"], email=c["email"], rol=exp["rol"], anios=exp["años"])

# 📥 Función para cargar certificaciones
def cargar_certificacion(tx, cert):
    fecha = cert["fecha_emision"].strftime("%Y-%m-%d")
    tx.run("""
        MERGE (curso:Curso {titulo: $curso})
        MERGE (cand:Candidato {email: $email})
        MERGE (cand)-[:TIENE_CERTIFICACION {fecha: $fecha, codigo: $codigo, modalidad: $modalidad}]->(curso)
    """, curso=cert["curso"], email=cert["candidato_email"],
         fecha=fecha, codigo=cert["codigo_certificado"], modalidad=cert["modalidad"])

# 📥 Función para cargar ofertas
def cargar_oferta(tx, o):
    tx.run("""
        MERGE (e:Empresa {nombre: $empresa})
        MERGE (of:Oferta {puesto: $puesto, empresa: $empresa})
        SET of.estado = $estado, of.ubicacion = $ubicacion, of.categoria = $categoria
        MERGE (e)-[:OFRECE]->(of)
    """, empresa=o["empresa"], puesto=o["puesto"], estado=o["estado"],
         ubicacion=o["ubicacion"], categoria=o["categoria"])

# 📥 Función para cargar procesos de selección
def cargar_proceso(tx, p):
    proc_id = f'{p["candidato_email"]}|{p["empresa"]}|{p["oferta_puesto"]}'
    fecha = p["fecha_inicio"].strftime("%Y-%m-%d")
    tx.run("""
        MERGE (cand:Candidato {email: $email})
        MERGE (of:Oferta {puesto: $puesto, empresa: $empresa})
        MERGE (proc:ProcesoSeleccion {id: $id})
        SET proc.estado = $estado, proc.fecha_inicio = $fecha
        MERGE (cand)-[:POSTULO_A]->(proc)
        MERGE (proc)-[:PARA_OFERTA]->(of)
    """, email=p["candidato_email"], puesto=p["oferta_puesto"],
         empresa=p["empresa"], estado=p["estado"], fecha=fecha, id=proc_id)

# 🔁 Ejecución del ETL
with neo4j.session() as session:
    for c in db["candidatos"].find():
        session.execute_write(cargar_candidato, c)
    for cert in db["certificaciones"].find():
        session.execute_write(cargar_certificacion, cert)
    for o in db["ofertas"].find():
        session.execute_write(cargar_oferta, o)
    for p in db["procesos_seleccion"].find():
        session.execute_write(cargar_proceso, p)

print("✅ ETL COMPLETO: MongoDB → Neo4j")
