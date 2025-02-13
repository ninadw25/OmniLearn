# filepath: /pdf-learning-assistant/pdf-learning-assistant/src/database/astra_client.py
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import os

class AstraClient:
    def __init__(self):
        self.cluster = None
        self.session = None

    def connect(self):
        try:
            cloud_config = {
                'secure_connect_bundle': os.getenv("ASTRA_SECURE_CONNECT_BUNDLE")
            }
            auth_provider = PlainTextAuthProvider(
                os.getenv("ASTRA_DB_CLIENT_ID"),
                os.getenv("ASTRA_DB_CLIENT_SECRET")
            )
            self.cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            self.session = self.cluster.connect()
            print("Connected to Astra DB")
        except Exception as e:
            print(f"Error connecting to Astra DB: {e}")

    def close(self):
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        print("Connection to Astra DB closed")