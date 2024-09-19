import streamlit as st
from model import ChatModel

import time

mod = ChatModel()

all_models = mod.display_models()

chat_model_list = []
embed_model_list = []
vision_model_list = []

accepted_file_types = ["png", "jpg", "jpeg", "bmp", "gif", "txt"]


for model in all_models:
    if "moondream" in model:
        vision_model_list.append(model)
    elif "llava" in model:
        vision_model_list.append(model)
    elif "embed" in model:
        embed_model_list.append(model)
    elif "hidden" in model:
        pass
    else:
        chat_model_list.append(model)


def model_radio_label(model_list, no_model_message=None):
    if model_list:
        return "Please choose a model"
    else:
        return no_model_message or "No model found."


chat_label = model_radio_label(
    chat_model_list, "No model found. Please pull from ollama"
)
embed_label = model_radio_label(embed_model_list)
vision_label = model_radio_label(vision_model_list)


def notice(message):
    st.session_state.notice = message


def scrape_website(url):
    print(url)


if "notice" not in st.session_state:
    st.session_state.notice = ""

if "processed_file" not in st.session_state:
    st.session_state.processed_file = None

with st.sidebar:
    chat_model = st.radio(label=chat_label, options=chat_model_list, index=None)
    if chat_model:
        mod.initialize_chat(chat_model)
        notice(f"{chat_model} active")

    embed_model = st.radio(label=embed_label, options=embed_model_list, index=None)
    if embed_model:
        mod.choose_embed_model(embed_model)

    vision_model = st.radio(label=vision_label, options=vision_model_list, index=None)
    if vision_model:
        mod.choose_vision_model(vision_model)

    if chat_model:
        docs = st.radio(
            label="File Selection Method", options=["Upload", "URL"], index=None
        )
        if docs == "Upload":
            file = st.file_uploader(label="Upload a File", type=accepted_file_types)
            if file is not None:
                file_name = file.name

                if st.session_state.processed_file != file_name:
                    bytes_data = file.getvalue()
                    response = mod.uploaded_file(file_name, bytes_data)
                    notice(response)

                    st.session_state.processed_file = file_name
        elif docs == "URL":
            url = st.text_input(label="Enter URL here")
            if st.button(label="Fetch URL"):
                scrape_website(url=url)

    if st.session_state.notice != "":
        st.info(st.session_state.notice)

st.title("Simple Chatbot")
st.caption("Author: kikoferrer")


def stream_response(response: str):
    for char in response:
        time.sleep(0.01)
        yield char


if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not chat_model:
        st.info("Choose a chat model first")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = mod.receive_user_message(prompt)

    st.session_state.messages.append({"role": chat_model, "content": response})
    with st.chat_message(chat_model):
        st.write_stream(stream_response(response))
