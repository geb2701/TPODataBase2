Instaladores:
    pip install fastapi uvicorn
    pip install pymongo
    pip install neo4j

Iniciar:
    python -m uvicorn main:app --reload

http://127.0.0.1:8000/docs#/


Consultas complicadas:
    Buscar Candidatos (ofertaId): Todo por neo
        Bucar oferta
        Buscamos los skills
        Buscamos los skills de nivel superior (mismo tipo pero mayor nivel)
        Buscar usuarios que matchen con almenos una skill
        Ver cuantos match tiene cada empelado y agrupar por cantidad de matchs
        devolver {
            5:[ids]
            1:[dis]
        }
        
    Ia:
        MATCH (oferta:Oferta {id: $ofertaId})-[:REQUIERE]->(skillReq:Skill)
        WITH oferta, collect(skillReq) AS skillsRequeridos

        UNWIND skillsRequeridos AS skillReq
        MATCH (skillSup:Skill)
        WHERE skillSup.tipo = skillReq.tipo AND skillSup.nivel >= skillReq.nivel

        WITH collect(DISTINCT skillSup.id) AS skillIds

        MATCH (usuario:Usuario)-[:POSEE]->(skill:Skill)
        WHERE skill.id IN skillIds

        WITH usuario, count(DISTINCT skill.id) AS matchCount
        ORDER BY matchCount DESC

        WITH matchCount, collect(usuario.id) AS usuarios
        RETURN apoc.map.fromPairs(collect([matchCount, usuarios])) AS resultado


    Buscar Candidatos Recomendados (ofertaId): Todo por neo
        Bucar oferta
        Buscamos los skills
        Buscamos los skills de nivel superior (mismo tipo pero mayor nivel)
        Buscar equipos de la empresa
        Buscar usuarios del equipo 
        Buscar usuarios recomendados por el usuario
        
        Ver cuantos match tiene cada usuario (recomendado) y agrupar por cantidad de matchs
        devolver {
            5:[ids]
            1:[dis]
        }

    Ia:
        // Busca la oferta y sus skills requeridos
        MATCH (oferta:Oferta {id: $ofertaId})-[:REQUIERE]->(skillReq:Skill)
        WITH oferta, collect(skillReq) AS skillsRequeridos

        // Busca skills de igual tipo y nivel superior
        UNWIND skillsRequeridos AS skillReq
        MATCH (skillSup:Skill)
        WHERE skillSup.tipo = skillReq.tipo AND skillSup.nivel >= skillReq.nivel
        WITH oferta, collect(DISTINCT skillSup.id) AS skillIds

        // Busca equipos de la empresa de la oferta
        MATCH (oferta)-[:PERTENECE_A]->(empresa:Empresa)<-[:PERTENECE_A]-(equipo:Equipo)
        WITH oferta, skillIds, collect(equipo) AS equipos

        // Busca usuarios de esos equipos
        UNWIND equipos AS equipo
        MATCH (usuarioEquipo:Usuario)-[:MIEMBRO_DE]->(equipo)
        WITH oferta, skillIds, collect(DISTINCT usuarioEquipo) AS usuariosEquipo

        // Busca usuarios recomendados por los usuarios del equipo
        UNWIND usuariosEquipo AS usuarioEquipo
        MATCH (usuarioEquipo)-[:RECOMIENDA]->(usuarioRecomendado:Usuario)
        WITH skillIds, collect(DISTINCT usuarioRecomendado) AS usuariosRecomendados

        // Calcula los matches de skills para los usuarios recomendados
        UNWIND usuariosRecomendados AS usuario
        MATCH (usuario)-[:POSEE]->(skill:Skill)
        WHERE skill.id IN skillIds
        WITH usuario, count(DISTINCT skill.id) AS matchCount
        ORDER BY matchCount DESC

        WITH matchCount, collect(usuario.id) AS usuarios
        RETURN apoc.map.fromPairs(collect([matchCount, usuarios])) AS resultado