from backend.chat import OllamaChat
from backend.database import Database
from backend.docs_process import Documents
from backend.utils import *
import json
import os
import glob
from PIL import Image


config_file = "config.json"


class Module:
    def __init__(self):
        if not os.path.exists(config_file):
            with open(config_file, "w") as f:
                defaul_config = {
                    "db_path": "database",
                    "file": "temp/*",
                    "chunk_size": 50,
                }
                json.dump(defaul_config, f)

        with open(config_file, "r") as f:
            self.config = json.load(f)

        self.chat_history = []
        self.chat = None
        self.vision_model = "moondream"
        self.embed_model = "nomic-embed-text"
        self.document = None
        self.db = None
        self.uploaded_file = None
        self.chat_list = []

    def receive_user_message(self, message: str) -> str:
        user_prompt = str(message)
        if user_prompt:
            self.chat_history.append(f"User: {user_prompt}")

            if self.uploaded_file:
                img_ext = ["png", "jpg", "jpeg", "bmp", "gif"]
                file_ext = self.uploaded_file.split("/")[-1].split(".")[-1]
                if file_ext not in img_ext:
                    if len(self.chat_history) == 1:
                        query_data = self.db.retrieval(user_prompt)
                    else:
                        modified_query = self.chat.history_aware_query(
                            self.chat_history
                        )
                        query_data = self.db.retrieval(modified_query)

                    response = self.chat.chat_loop(
                        prompt=self.chat_history,
                        file=self.uploaded_file,
                        query_data=query_data,
                    )
                    return response
                elif file_ext in img_ext:
                    response = self.chat.chat_loop(
                        prompt=self.chat_history, file=self.uploaded_file
                    )
                    return response
            else:
                response = self.chat.chat_loop(prompt=self.chat_history)
                return response
        else:
            return "No Message received"

    def display_models(self) -> str | list:
        all_models = display_models()

        for model in all_models:
            if model != "moondream":
                if "llava" not in model:
                    if "embed" not in model:
                        self.chat_list.append(model)

        if not self.chat_list:
            return "There are no models for chat. Please pull a model from Ollama"
        else:
            return all_models

    def initialize_chat(self, model: str) -> str:
        self.chat = OllamaChat(chat_model=model, vision_model=self.vision_model)
        return f"Now using {model}"

    def choose_embed_model(self, model: str) -> str:
        self.embed_model = model
        return f"Embed model changed to {model}"

    def choose_vision_model(self, model: str) -> str:
        self.vision_model = model
        return f"Vision model changed to {model}"

    def uploaded_file(self, filename: str, decoded_contents: bytes) -> str:
        if self.chat:
            if filename and decoded_contents:
                if glob.glob(self.config["file"]):
                    os.remove(glob.glob(self.config["file"])[0])

                doc_path = "temp"

                if not os.path.exists(doc_path):
                    os.makedirs(doc_path)

                with open(os.path.join(doc_path, filename), "wb") as f:
                    f.write(decoded_contents)

                file_ext = filename.split(".")[-1]
                self.uploaded_file = glob.glob(self.config["file"])[0]

                img_ext = ["png", "jpg", "jpeg", "bmp", "gif"]
                if file_ext not in img_ext:
                    self.document = Documents(
                        self.uploaded_file, self.config["chunk_size"]
                    )
                    documents = self.document.cleaning_process()
                    self.db = Database(
                        self.config["db_path"], documents, self.embed_model
                    )
                    self.db.init_collection(filename)
                    self.db.embedding()
                    return f"File: {filename}, successfully uploaded"
                elif file_ext in img_ext:
                    return f"Image: {filename}, successfully uploaded"

        else:
            return "Choose a model first"
