import ollama
from backend.utils import display_models


class OllamaChat:
    def __init__(self, chat_model=None, vision_model="moondream"):
        self.chat_model = chat_model
        self.vision_model = vision_model

    def chat_loop(self, prompt: list, file: str = None, query_data: str = None) -> str:
        if file:
            print(file)
            if query_data:
                if len(prompt) == 1:
                    user_prompt = f"respond to this message naturally: '{prompt[0]}' using this provided data: '{query_data}'"
                    message = [{"role": "user", "content": user_prompt}]
                else:
                    message_history = "\n".join(prompt[:-1])
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
                    message_history = "\n".join(prompt[:-1])
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
                message_history = "\n".join(prompt[:-1])
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
            vision_model = self.vision_model
            if vision_model not in model_list:
                print(f"Downloading vision model: {vision_model}")
                ollama.pull(vision_model)
                print(f"Vision Model downloaded: {vision_model}")
            prompt = "Describe the image with as much detail as you can"
            response = ollama.generate(
                model=vision_model, prompt=prompt, images=[images]
            )
            print(response["response"])
            return response["response"]

    def history_aware_query(self, prompt: list) -> str:
        message_history = "\n".join(prompt)
        user_prompt = f"Given this conversation history: '{message_history}', generate a search query to look up  in order to get information relevant to the conversation"
        message = [
            {
                "role": "user",
                "content": user_prompt,
            }
        ]
        response = ollama.chat(model=self.chat_model, messages=message)
        return response["message"]["content"]
