# En cualquier archivo donde necesites la conexión
from Services.DatabaseConfig import DatabaseConfig

db_config = DatabaseConfig()
mongo_db = db_config.get_mongo_db()
neo4j_driver = db_config.get_neo4j_driver()