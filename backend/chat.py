import ollama
import re
from backend.utils import display_models


class OllamaChat:
    def __init__(self, chat_model, vision_model=None):
        self.chat_model = chat_model
        self.vision_model = vision_model

    def chat_loop(
        self, prompt: list[dict], file: str = None, query_data: str = None
    ) -> str:
        if file:
            if query_data:
                if len(prompt) == 1:
                    last_message = prompt[0]
                    user_message = last_message["content"]
                    user_prompt = f"using this provided context: '{query_data}', respond to my message: '{prompt[0]}'. Ensure your response is natural to the flow of the conversation."
                    messages = [{"role": "user", "content": user_prompt}]
                else:
                    messages = prompt[:-1]
                    last_message = prompt[-1]
                    user_message = last_message["content"]
                    user_prompt = f"using this provided context: '{query_data}' respond to my message: '{user_message}'. Ensure your response is natural to the flow of the conversation."
                    message = {
                        "role": "user",
                        "content": user_prompt,
                    }
                    messages.append(message)
            else:
                image_description = self.vision_model_chat(file)
                if len(prompt) == 1:
                    last_message = prompt[0]
                    user_message = last_message["content"]
                    user_prompt = f"using this provided context: '{image_description}', respond to my message: '{user_message}'. Ensure your response is natural to the flow of the conversation."
                    messages = [{"role": "user", "content": user_prompt}]
                else:
                    messages = prompt[:-1]
                    last_message = prompt[-1]
                    user_message = last_message["content"]
                    user_prompt = f"using this provided context: '{image_description}', respond to my message: '{user_message}'. Ensure your response is natural to the flow of the conversation."
                    message = {
                        "role": "user",
                        "content": user_prompt,
                    }
                    messages.append(message)
        else:
            messages = prompt
        response = self.chain_of_thought(messages)
        # answer = ollama.chat(model=self.chat_model, messages=messages)
        # response = answer["message"]["content"]
        return response

    def vision_model_chat(self, file):
        with open(file, "rb") as i:
            images = i.read()
            model_list = display_models()
            vision_model = self.vision_model
            vision_model_count = 0

            for model in model_list:
                if "llava" in model:
                    vision_model_count += 1
                if "moondream" in model:
                    vision_model_count += 1

            if vision_model_count == 0 and self.vision_model is None:
                default_vision_model = "moondream"
                print(f"Downloading vision model: {default_vision_model}")
                ollama.pull(default_vision_model)
                print(f"Vision Model downloaded: {default_vision_model}")
                vision_model = default_vision_model
            prompt = "Describe the image with as much detail as you can"
            response = ollama.generate(
                model=vision_model, prompt=prompt, images=[images]
            )
            print(response["response"])
            return response["response"]

    def history_aware_query(self, prompt: list) -> str:
        message_history = prompt[:-1]
        last_message = prompt[-1]
        user_message = last_message["content"]
        user_prompt = f"generate a specific and detailed search query from this message: {user_message}, with regards to the conversation so far. Only respond with the query"
        message = {
            "role": "user",
            "content": user_prompt,
        }
        messages = message_history.append(message)
        response = ollama.chat(model=self.chat_model, messages=messages)
        return response["message"]["content"]

    def rerank_query_data(self, user_prompt, query_data: str) -> str:
        rerank_message = f"reorder the data from most relevant to least relevant to the query. seperate each data with newlines. Do not change the contents of the data and reorder them with the original content. This is the query: '{user_prompt}'. This is the data: {query_data}"
        messages = [{"role": "user", "content": rerank_message}]
        response = ollama.chat(model=self.chat_model, messages=messages)
        return response["message"]["content"]

    def chain_of_thought(self, prompt_history: list) -> str:
        prompt = prompt_history[-1]
        message = prompt["content"]

        if len(prompt_history) == 1:
            history = []
        else:
            history = prompt_history[:-1]

        initial_res = ollama.chat(model="Test", messages=prompt_history)
        initial_response = initial_res["message"]["content"]
        print(f"{initial_response}\n\n")

        reflection_message = f"Answer this question: '{message}', by reflecting on this response: '{initial_response}', "
        reflection_messages = {"role": "user", "content": reflection_message}
        history.append(reflection_messages)

        reflection_res = ollama.chat(model="hidden-Reflection", messages=history)
        reflection_response = reflection_res["message"]["content"]

        match = re.search(
            r"<output>(.*?)(?:</output>|$)", reflection_response, re.DOTALL
        )
        output = match.group(1).strip() if match else reflection_response

        final_message = f"respond naturally from this message: '{message}', using this answer as basis: '{output}'"
        final_messages = {"role": "user", "content": final_message}
        final_history = history[:-1]
        final_history.append(final_messages)

        final_output = ollama.chat(model=self.chat_model, messages=final_history)

        return final_output["message"]["content"]
