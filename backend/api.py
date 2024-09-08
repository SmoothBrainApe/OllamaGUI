from fastapi import FastAPI, File, UploadFile
from backend.module import Module
import base64


app = FastAPI()
mod = Module()


@app.post("/chat/send")
async def receive_message(message_payload: dict) -> dict:
    if message_payload["message"]:
        message = message_payload["message"]
        response = mod.receive_user_message(message)
        return {"message": response}
    else:
        return {"message": "message cannot be empty"}


@app.get("/chat/models")
def send_models_list() -> dict[str | list]:
    response = mod.display_models()
    return {"message": response}


@app.post("/chat/chat_model")
def chat_model(model_payload: dict) -> dict:
    if model_payload["message"]:
        model = model_payload["message"]
        mod.initialize_chat(model)
        message = f"Now using {model}"
        return {"message": message}
    else:
        return {"message": "Please choose a model"}


@app.post("/chat/embed_model")
def embed_model(model_payload: dict) -> dict:
    model = model_payload["message"]
    response = mod.choose_embed_model(model)
    return {"message": response}


@app.post("/chat/vision_model")
def vision_model(model_payload: dict) -> dict:
    model = model_payload["message"]
    response = mod.choose_vision_model(model)
    return {"message": response}


@app.post("/chat/upload")
def upload_file(file: UploadFile = File(...)) -> dict:
    if file:
        contents = await file.read()
        decoded_contents = base64.b64decode(contents)
        filename = file.filename
        response = mod.uploaded_file(filename, decoded_contents)
        return {"message": response}
    else:
        return {"message": "file not uploaded."}


@app.delete("/chat/delete_file")
def delete_uploaded_file():
    pass


@app.delete("/chat/clear_history")
async def clear_history():
    pass
