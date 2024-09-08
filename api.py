from flask import Blueprint, request, jsonify
from app import app
from model import ChatModel
import base64

api = Blueprint("api", __name__)

mod = ChatModel()


@api.route("/chat/message", methods=["POST"])
def receive_message():
    payload = request.get_json()
    if payload.get("message"):
        message = payload["message"]
        response = mod.receive_user_message(message=message)
        return jsonify({"message": response})
    else:
        return jsonify({"message": "message cannot be empty"})


@api.route("/chat/models", methods=["GET"])
def send_models_list():
    response = mod.display_models()
    return jsonify({"message": response})


@api.route("/chat/models/pull", methods=["POST"])
def pull_model():
    payload = request.get_json()
    if payload.get("message"):
        model = payload["message"]
        response = mod.pull_model(model)
        return jsonify({"message": response})


@api.route("/chat/models/chat", methods=["POST"])
def chat_model():
    payload = request.get_json()
    if payload.get("message"):
        model = payload["message"]
        mod.initialize_chat(model)
        message = f"Now using {model}"
        return jsonify({"message": message})
    else:
        return jsonify({"message": "Please choose a model"})


@api.route("/chat/models/embed", methods=["POST"])
def embed_model():
    payload = request.get_json()
    model = payload["message"]
    response = mod.choose_embed_model(model)
    return jsonify({"message": response})


@api.route("/chat/models/vision", methods=["POST"])
def vision_model():
    payload = request.get_json()
    model = payload["message"]
    response = mod.choose_vision_model(model)
    return jsonify({"message": response})


@api.route("/chat/file/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")
    filename = request.form.get("filename")
    if file and filename:
        decoded_contents = base64.b64decode(file.read())
        response = mod.uploaded_file(filename, decoded_contents)
        return jsonify({"message": response})
    else:
        return jsonify({"message": "file not uploaded."})


@api.route("/chat/modelfile/get", methods=["GET"])
def display_modelfile():
    payload = request.get_json()
    model_name = payload.get("message")
    response = mod.display_modelfile(model_name)
    return jsonify({"message": response})


@api.route("/chat/modelfile/create", methods=["PUT"])
def create_modelfile():
    payload = request.get_json()
    model_name = payload.get("name")
    modelfile = payload.get("modelfile")
    response = mod.create_modelfile(model_name, modelfile)
    return jsonify({"message": response})


@api.route("/chat/file/delete", methods=["DELETE"])
def delete_uploaded_file():
    response = mod.delete_file()
    return jsonify({"message": response})


@api.route("/chat/message/clear", methods=["DELETE"])
def clear_history():
    response = mod.clear_chat_history()
    return jsonify({"message": response})


app.register_blueprint(api)
