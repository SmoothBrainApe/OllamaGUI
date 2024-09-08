from fastapi import FastAPI, File, UploadFile
from backend.module import Module
import base64


app = FastAPI()
mod = Module()


@app.post("/chat/message")
async def receive_message(payload: dict) -> dict:
    if payload["message"]:
        message = payload["message"]
        response = mod.receive_user_message(message)
        return {"message": response}
    else:
        return {"message": "message cannot be empty"}


@app.get("/chat/models")
async def send_models_list() -> dict[str | list]:
    response = mod.display_models()
    return {"message": response}


@app.post("/chat/models/pull")
async def pull_model(payload: dict) -> dict:
    if payload["message"]:
        model = payload["message"]
        response = mod.pull_model(model)
        return {"message": response}


@app.post("/chat/models/chat")
async def chat_model(payload: dict) -> dict:
    if payload["message"]:
        model = payload["message"]
        mod.initialize_chat(model)
        message = f"Now using {model}"
        return {"message": message}
    else:
        return {"message": "Please choose a model"}


@app.post("/chat/models/embed")
async def embed_model(payload: dict) -> dict:
    model = payload["message"]
    response = mod.choose_embed_model(model)
    return {"message": response}


@app.post("/chat/models/vision")
async def vision_model(payload: dict) -> dict:
    model = payload["message"]
    response = mod.choose_vision_model(model)
    return {"message": response}


@app.post("/chat/file/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    if file:
        contents = await file.read()
        decoded_contents = base64.b64decode(contents)
        filename = file.filename
        response = mod.uploaded_file(filename, decoded_contents)
        return {"message": response}
    else:
        return {"message": "file not uploaded."}


@app.get("/chat/modelfile/<model_name>")
async def display_modelfile(payload) -> dict:
    model_name = payload["message"]
    response = mod.display_modelfile(model_name)
    return {"message": response}


@app.put("/chat/modelfile/<model_name>")
async def create_modelfile(payload: dict) -> dict:
    model_name = payload["name"]
    modelfile = payload["modelfile"]
    response = mod.create_modelfile(model_name, modelfile)
    return {"message": response}


@app.delete("/chat/file/delete")
async def delete_uploaded_file() -> dict:
    response = mod.delete_file()
    return {"message": response}


@app.delete("/chat/message/clear")
async def clear_history() -> dict:
    response = mod.clear_chat_history()
    return {"message": response}
