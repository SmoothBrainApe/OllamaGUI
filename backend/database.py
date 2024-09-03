import chromadb
import ollama
import math
import os
from backend.utils import display_models


class Database:
    def __init__(self, db_path: str, documents: list):
        model_list = display_models()
        if "nomic-embed-text" not in model_list:
            print(f"Downloading vision model: {self.embed_model}")
            ollama.pull(self.embed_model)
            print(f"Vision Model downloaded: {self.embed_model}")
        self.db_path = db_path
        self.collection = None
        self.embed_model = "nomic-embed-text"
        self.documents = documents
        try:
            if not os.path.exists(self.db_path):
                os.makedirs(self.db_path)
            self.db = chromadb.PersistentClient(path=self.db_path)
            print("Database created")
        except Exception as e:
            print(f"Error has occured: {e}")

    def init_collection(self, file: str):
        print("Collection created")
        file_name = file.split("/")[-1]
        name = file_name.split(".")[0]
        while True:
            try:
                self.collection = self.db.create_collection(name=name)
                break
            except chromadb.db.base.UniqueConstraintError:
                self.db.delete_collection(name=name)
            except Exception as e:
                print(f"Error has occured: {e}")
                break

    def embedding(self):
        for i, docs in enumerate(self.documents):
            try:
                embed_response = ollama.embeddings(model=self.embed_model, prompt=docs)
                embed = embed_response["embedding"]
                self.collection.upsert(ids=str(i), embeddings=[embed], documents=[docs])
            except Exception as e:
                print(f"Error embedding document {i}: {e}")
        print("All embeddings created")

    def retrieval(self, prompt: str) -> str:
        n_results = math.floor(len(self.documents) / 8)
        retrieve_response = ollama.embeddings(model=self.embed_model, prompt=prompt)
        retrieve_results = self.collection.query(
            query_embeddings=[retrieve_response["embedding"]],
            n_results=n_results,
        )
        lines = retrieve_results["documents"][0]
        retrieved_data = "\n".join(lines)
        print("query data retrieved")
        return retrieved_data
