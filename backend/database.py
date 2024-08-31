import chromadb
import ollama
import math


class Database:
    def __init__(self, db_path, embed_model, documents):
        self.db_path = db_path
        self.collection = None
        self.embed_model = embed_model
        self.documents = documents
        try:
            self.db = chromadb.PersistentClient(path=self.db_path)
        except Exception as e:
            print(f"Error has occured: {e}")

    def init_collection(self, file):
        file_name = file.split("/")[-1]
        name = file_name.split(".")[0]
        try:
            self.collection = self.db.create_collection(name=name)
        except chromadb.db.base.UniqueConstraintError:
            self.collection = self.db.get_collection(name=name)
        except Exception as e:
            print(f"Error has occured: {e}")

    def embedding(self):
        for i, docs in enumerate(self.documents):
            try:
                embed_response = ollama.embeddings(model=self.embed_model, prompt=docs)
                embed = embed_response["embedding"]
                self.collection.upsert(ids=str(i), embeddings=[embed], documents=docs)
            except Exception as e:
                print(f"Error has occured: {e}")

    def retrieval(self, message: list) -> str:
        try:
            prompt = message[-1]["content"]
            n_results = math.floor(len(self.documents) / 4) * 3
            retrieve_response = ollama.embeddings(model=self.embed_model, prompt=prompt)
            retrieve_results = self.collection.query(
                query_embeddings=[retrieve_response["embedding"]],
                n_results=n_results,
            )
            lines = retrieve_results["documents"][0]
            retrieved_data = "\n".join(lines)
            return retrieved_data
        except Exception as e:
            print(f"Error has occured: {e}")
            return None
