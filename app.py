from flask import Flask, render_template, jsonify, request
from model import ChatModel
import base64
import json

app = Flask(__name__)
mod = ChatModel()

# APP Routes


@app.route("/")
def index():
    return render_template("index.html")


# API Endpoints


@app.route("/chat/message", methods=["POST"])
def receive_message():
    payload = request.get_json()
    if payload:
        message = payload.get("message")
        response = mod.receive_user_message(message=message)
        return jsonify({"message": response})
    else:
        return jsonify({"message": "message cannot be empty"})


@app.route("/chat/models", methods=["GET"])
def send_models_list():
    response = mod.display_models()
    return jsonify({"message": response})


@app.route("/chat/models/pull", methods=["POST"])
def pull_model():
    payload = request.get_json()
    if payload.get("message"):
        models = payload["message"]
        response = mod.pull_model(models)
        return jsonify({"message": response})


@app.route("/chat/models/chat", methods=["POST"])
def chat_model():
    payload = request.get_json()
    if payload.get("message"):
        models = payload["message"]
        mod.initialize_chat(models)
        message = f"Now using {models}"
        return jsonify({"message": message})
    else:
        return jsonify({"message": "Please choose a model"})


@app.route("/chat/models/embed", methods=["POST"])
def embed_model():
    payload = request.get_json()
    models = payload["message"]
    response = mod.choose_embed_model(models)
    return jsonify({"message": response})


@app.route("/chat/models/vision", methods=["POST"])
def vision_model():
    payload = request.get_json()
    models = payload["message"]
    response = mod.choose_vision_model(models)
    return jsonify({"message": response})


@app.route("/chat/file/upload", methods=["POST"])
def upload_file():
    try:
        data = request.get_json()
        filename = data["filename"]
        filedata = data["filedata"]

        decoded_contents = base64.b64decode(filedata)

        response = mod.uploaded_file(
            filename=filename, decoded_contents=decoded_contents
        )
        print(response)

        return jsonify({"message": "File received"})
    except Exception as e:
        return jsonify({"message": "Error uploading file.", "error": str(e)}), 500


@app.route("/chat/modelfile/get", methods=["GET"])
def display_modelfile():
    payload = request.get_json()
    model_name = payload.get("message")
    response = mod.display_modelfile(model_name)
    return jsonify({"message": response})


@app.route("/chat/modelfile/create", methods=["PUT"])
def create_modelfile():
    payload = request.get_json()
    model_name = payload.get("name")
    modelfile = payload.get("modelfile")
    response = mod.create_modelfile(model_name, modelfile)
    return jsonify({"message": response})


@app.route("/chat/file/delete", methods=["DELETE"])
def delete_uploaded_file():
    response = mod.delete_file()
    return jsonify({"message": response})


@app.route("/chat/message/clear", methods=["DELETE"])
def clear_history():
    response = mod.clear_chat_history()
    return jsonify({"message": response})


if __name__ == "__main__":
    app.run(debug=True)
