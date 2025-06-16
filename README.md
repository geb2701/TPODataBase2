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
