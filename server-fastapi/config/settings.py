import os
class Settings:
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    VECTOR_STORE_TABLE = "course_materials"
    CONSISTENCY_LEVEL = "LOCAL_ONE"
    
    @property
    def astra_db_config(self):
        return {
            "token": os.getenv("ASTRADB_API_KEY"),
            "database_id": os.getenv("ASTRADB_DATABASE_ID"),
            "keyspace": os.getenv("ASTRADB_KEYSPACE")
        }

settings = Settings()