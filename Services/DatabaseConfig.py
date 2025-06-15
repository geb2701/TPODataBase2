from pymongo import MongoClient
from neo4j import GraphDatabase

class DatabaseConfig:
    def __init__(self):
        # MongoDB
        self.mongo_client = MongoClient("mongodb+srv://TPODataBase2:WcTpJOR9ZuFPxNmW@tpodatabase2.dvx531v.mongodb.net/")
        self.mongo_db = self.mongo_client["talentum"]

        # Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            "neo4j+ssc://bd136a15.databases.neo4j.io",
            auth=("neo4j", "0czpIif4DzPnO1prJ8QjyfSBHut1LKTo2ZeX-Y4rndQ")
        )
        self.neo4j_driver.verify_connectivity()

    def get_mongo_db(self):
        return self.mongo_db

    def get_neo4j_driver(self):
        return self.neo4j_driver