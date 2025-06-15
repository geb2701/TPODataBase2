from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()
driver = db_config.get_neo4j_driver()

class ProcesoSeleccionService:

    @staticmethod
    def crear_proceso(data):
        with driver.session() as session:
            result = session.run("""
                CREATE (p:ProcesoSeleccion {
                    empresa_id: $empresa_id,
                    oferta_id: $oferta_id,
                    candidato_id: $candidato_id,
                    reclutador_id: $reclutador_id,
                    estado: $estado,
                    historial: $historial
                })
                RETURN id(p) AS id
            """, **data)
            record = result.single()
            return {**data, "id": str(record["id"])}

    @staticmethod
    def listar_procesos():
        with driver.session() as session:
            result = session.run("MATCH (p:ProcesoSeleccion) RETURN id(p) AS id, p")
            return [{"id": str(r["id"]), **r["p"]} for r in result]

    @staticmethod
    def obtener_por_id(proceso_id):
        with driver.session() as session:
            result = session.run("MATCH (p) WHERE id(p) = $id RETURN p", id=int(proceso_id))
            record = result.single()
            if not record:
                return None
            p = record["p"]
            return {"id": proceso_id, **p}

    @staticmethod
    def actualizar_proceso(proceso_id, data):
        set_clause = ", ".join([f"p.{k} = ${k}" for k in data])
        query = f"""
            MATCH (p) WHERE id(p) = $id
            SET {set_clause}
            RETURN p
        """
        with driver.session() as session:
            session.run(query, id=int(proceso_id), **data)
        return ProcesoSeleccionService.obtener_por_id(proceso_id)

    @staticmethod
    def eliminar_proceso(proceso_id):
        with driver.session() as session:
            session.run("MATCH (p) WHERE id(p) = $id DETACH DELETE p", id=int(proceso_id))
