import chromadb
import ollama
import math
import os
from backend.utils import display_models


class Database:
    def __init__(self, db_path: str, documents: list, embed_model: str = None):
        self.db_path = db_path
        self.collection = None
        self.embed_model = embed_model
        self.documents = documents
        self.total_embeddings = 0

        embed_model_count = 0
        model_list = display_models()
        for model in model_list:
            if "embed" in model:
                embed_model_count += 1

        if embed_model_count == 0 and self.embed_model is None:
            default_embed_model = "nomic-embed-text"
            print(f"Downloading default embed model: {default_embed_model}")
            ollama.pull(default_embed_model)
            print(f"Embed Model downloaded: {default_embed_model}")
            self.embed_model = default_embed_model

        try:
            if not os.path.exists(self.db_path):
                os.makedirs(self.db_path)
            self.db = chromadb.PersistentClient(path=self.db_path)
            print("Database created")
        except Exception as e:
            print(f"Error has occured: {e}")

    def init_collection(self, file_name: str):
        print("Collection created")
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
                self.total_embeddings += 1
                print(i)
                print(self.total_embeddings)
                embed_response = ollama.embeddings(model=self.embed_model, prompt=docs)
                embed = embed_response["embedding"]
                self.collection.upsert(ids=str(i), embeddings=[embed], documents=[docs])
            except Exception as e:
                print(f"Error embedding document {i}: {e}")
        print("All embeddings created")

    def retrieval(self, prompt: str) -> str:
        if self.total_embeddings <= 10:
            n_results = math.floor(len(self.documents) / 8) * 3
        else:
            n_results = self.total_embeddings
        retrieve_response = ollama.embeddings(model=self.embed_model, prompt=prompt)
        retrieve_results = self.collection.query(
            query_embeddings=[retrieve_response["embedding"]],
            n_results=n_results,
        )
        lines = retrieve_results["documents"][0]
        retrieved_data = "\n".join(lines)
        print("query data retrieved")
        return retrieved_data
