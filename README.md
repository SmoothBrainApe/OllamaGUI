Ollama with python and tkinter

Features:

> Powered by Ollama. Existing ollama models will automatically be detected.
> Regular chat
> Chat with your documents (Will activate after uploading a file)
> Currently only supports .txt files. Will add support for more file types in the future.
> Chat with an image with vision models. Just upload the image and start chatting.
> Pull models and create modefile in the settings.

Install:

`git clone https://github.com/kikoferrer/OllamaGUI.git`
`cd OllamaGUI`

`python -m venv venv` (optional but recommended)
`source venv/bin/activate` (skip if you did not create a venv)

`pip install -r requirements.txt`
`python main.py`

Todo List:
[] Add support for multiple file types:

> [] PDF
> [] CSV
> [] Excel Sheets
> [] Documents
> [] Website links

[] improve RAG accuracy
[] improve GUI. It is very ugly
[] implement logging for errors
[] bug hunting and bug fixes. Feedbacks are welcome

"It ain't much but its honest work."
