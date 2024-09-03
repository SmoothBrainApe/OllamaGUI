import ollama


class OllamChat:
    def __init__(self, chat_model=None):
        self.chat_model = chat_model
        self.vision_model = None

    def chat_loop(self, prompt: list, file: str = None, query_data: str = None) -> str:
        if file:
            print(file)
            if query_data:
                if len(prompt) == 1:
                    user_prompt = f"respond to this message naturally: '{prompt[0]}' using this provided data: '{query_data}'"
                    message = [{"role": "user", "content": user_prompt}]
                else:
                    message_history = "\n".join(prompt[:-1]) + prompt[-1]
                    user_message = prompt[-1]
                    user_prompt = f"respond to this message naturally: '{user_message[6:]}' using this provided data: '{query_data}' while considering this chat history: '{message_history}'"
                    message = [
                        {
                            "role": "user",
                            "content": user_prompt,
                        }
                    ]
            else:
                image_description = self.vision_model_chat(file)
                if len(prompt) == 1:
                    user_prompt = f"respond to this message naturally: '{prompt[0]}' using this provided data: '{image_description}'"
                    message = [{"role": "user", "content": user_prompt}]
                else:
                    message_history = "\n".join(prompt[:-1]) + prompt[-1]
                    user_message = prompt[-1]
                    user_prompt = f"respond to this message naturally: '{user_message[6:]}' using this provided data: '{image_description}' while considering this chat history: {message_history}"
                    message = [
                        {
                            "role": "user",
                            "content": user_prompt,
                        }
                    ]
        else:
            if len(prompt) == 1:
                message = [
                    {
                        "role": "user",
                        "content": prompt[0],
                    }
                ]
            else:
                message_history = "\n".join(prompt[:-1]) + prompt[-1]
                user_message = prompt[-1]
                user_prompt = f"respond to this message naturally: '{user_message[6:]}' while considering this chat history: '{message_history}'"
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

    def vision_model_chat(self, file):
        with open(file, "rb") as i:
            images = i.read()
            model_list = display_models()
            vision_model = "moondream"
            if vision_model not in model_list:
                ollama.pull(vision_model)
            prompt = "Describe the image with as much detail as you can"
            response = ollama.generate(
                model=vision_model, prompt=prompt, images=[images]
            )
            print(response["response"])
            return response["response"]


def display_models() -> list:
    ollama_list = ollama.list()
    models_dict = ollama_list["models"]

    models = []
    for model in models_dict:
        model_data = model["name"]
        model_name = model_data.split(":")
        models.append(model_name[0])

    return models


def pull_model(model_name: str) -> str:
    ollama.pull(model_name)
    return f"Model {model_name} pulled successfully!"


def show_model(self, model_name: str):
    return ollama.show(model_name)


def create_modelfile(self, model_name: str, modelfile: str):
    ollama.create(model=model_name, modelfile=modelfile)
