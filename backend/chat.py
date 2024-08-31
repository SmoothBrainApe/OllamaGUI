import ollama


def display_models() -> list:
    ollama_list = ollama.list()
    models_dict = ollama_list["models"]

    models = []
    for model in models_dict:
        model_data = model["name"]
        model_name = model_data.split(":")
        models.append(model_name[0])

    return models


class OllamChat:
    def __init__(self, chat_model=None):
        self.chat_model = chat_model
        self.embed_model = None

    def pull_model(self, name: str):
        return ollama.pull(name)

    def show_model(self, name: str):
        return ollama.show(name)

    def create_modelfile(self, name: str, modelfile: str):
        ollama.create(model=name, modelfile=modelfile)

    def simple_chat(self, prompt: list) -> str:
        if len(prompt) == 1:
            user_prompt = prompt[0]
            message = [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ]
        else:
            message_history = "\n".join(prompt[:-1]) + prompt[-1]
            user_prompt = f"respond to this message {prompt[-1]} while considering this chat history: {message_history}"
            message = [
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ]
        stream = ollama.chat(
            model=self.chat_model,
            messages=message,
            stream=True,
        )

        for word in stream:
            yield word["message"]["content"]

    def embedding(self, prompt: str, model: str):
        self.embed_model = model
        response = ollama.embeddings(model=self.embed_model, prompt=prompt)
        return response["embedding"]
