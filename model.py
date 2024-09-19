from backend.chat import OllamaChat
from backend.database import Database
from backend.docs_process import Documents
from backend.utils import *
import os
import ollama


class ChatModel:
    def __init__(self):
        self.chat_history = []
        self.chat = None
        self.vision_model = "moondream"
        self.embed_model = "nomic-embed-text"
        self.document = None
        self.db = None
        self.db_path = "database"
        self.file_name = None
        self.file_data = None
        self.chat_list = []

    def receive_user_message(self, message: str) -> str:
        user_prompt = str(message)
        if user_prompt:
            if user_prompt.startswith("[RAG]"):
                for_history = user_prompt[5:].strip()
                history_user_message = {
                    "role": "user",
                    "content": for_history,
                }
                self.chat_history.append(history_user_message)
                img_ext = ["png", "jpg", "jpeg", "bmp", "gif"]
                file_ext = self.file_name.split("/")[-1].split(".")[-1]
                if file_ext not in img_ext:
                    if len(self.chat_history) == 1:
                        query_data = self.db.retrieval(user_prompt)
                        print(query_data)
                        reranked_query = self.chat.rerank_query_data(
                            query_data=query_data, user_prompt=user_prompt
                        )
                        print(f"\n\n{reranked_query}")
                    else:
                        modified_query = self.chat.history_aware_query(
                            self.chat_history
                        )
                        query_data = self.db.retrieval(modified_query)
                        print(query_data)
                        reranked_query = self.chat.rerank_query_data(
                            query_data=query_data, user_prompt=user_prompt
                        )
                        print(f"\n\n{reranked_query}")

                    response = self.chat.chat_loop(
                        prompt=self.chat_history,
                        file=self.file_name,
                        query_data=query_data,
                    )
                    history_response = {
                        "role": "assistant",
                        "content": response,
                    }
                    self.chat_history.append(history_response)
                    return response
                elif file_ext in img_ext:
                    response = self.chat.chat_loop(
                        prompt=self.chat_history, file=self.file_data
                    )
                    history_response = {
                        "role": "assistant",
                        "content": response,
                    }
                    self.chat_history.append(history_response)
                    return response
            else:
                history_user_message = {
                    "role": "user",
                    "content": user_prompt.strip(),
                }
                self.chat_history.append(history_user_message)
                response = self.chat.chat_loop(prompt=self.chat_history)
                history_response = {"role": "assistant", "content": response}
                self.chat_history.append(history_response)
                return response
        else:
            return "No Message received"

    def display_models(self) -> str | list:
        all_models = display_models()

        for model in all_models:
            if "moondream" not in model:
                if "llava" not in model:
                    if "embed" not in model:
                        if "hidden" not in model:
                            self.chat_list.append(model)

        if not self.chat_list:
            return "There are no models for chat. Please pull a model from Ollama"
        else:
            return all_models

    def pull_model(self, model_name: str) -> str:
        ollama.pull(model_name)
        return f"Model {model_name} pulled successfully!"

    def initialize_chat(self, model: str) -> str:
        self.chat = OllamaChat(chat_model=model, vision_model=self.vision_model)
        return f"Now using {model}"

    def choose_embed_model(self, model: str) -> str:
        self.embed_model = model
        return f"Embed model changed to {model}"

    def choose_vision_model(self, model: str) -> str:
        self.vision_model = model
        return f"Vision model changed to {model}"

    def uploaded_file(self, filename: str, bytes_data: bytes) -> str:
        if filename and bytes_data:
            self.file_name = filename
            file_ext = filename.split(".")[-1]
            img_ext = ["png", "jpg", "jpeg", "bmp", "gif"]
            if file_ext not in img_ext:
                if file_ext == "txt":
                    decoded_contents = bytes_data.decode("utf-8")
                    self.document = Documents(decoded_contents)
                    documents = self.document.cleaning_process()
                    self.db = Database(self.db_path, documents, self.embed_model)
                    self.db.init_collection(filename)
                    self.db.embedding()
                    return f"File: {filename}, successfully uploaded"
            elif file_ext in img_ext:
                self.file_data = bytes_data
                return f"Image: {filename}, successfully uploaded"

    def display_modelfile(self, model_name: str) -> str:
        modelfile_path = "../modelfiles"

        if not os.path.exists(modelfile_path):
            os.makedirs(modelfile_path)

        if not os.listdir(modelfile_path):
            return "No modelfile found! Create a modelfile first!"

        modelfile = f"{modelfile_path}/{model_name}"

        if not os.path.exists(modelfile):
            return f"Modelfile for {model_name} not found! Create one first!"

        with open(modelfile, "r") as m:
            modelfile_text = m.read()

        return modelfile_text

    def create_modelfile(self, model_name: str, modelfile: str) -> str:
        ollama.create(model=model_name, modelfile=modelfile)
        return f"modelfile for {model_name} created!"

    def delete_file(self) -> str:
        if self.uploaded_file:
            os.remove(self.uploaded_file)
            return "Uploaded file deleted"

    def clear_chat_history(self) -> str:
        if self.chat_history:
            self.chat_history = []
            return "Chat history cleared"
