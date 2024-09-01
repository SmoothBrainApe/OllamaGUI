import tkinter as tk
from tkinter import filedialog
import signal
import atexit
import shutil
import os
import json
import glob
from backend.chat import OllamChat, display_models
from backend.database import Database
from backend.docs_process import Documents
from backend.utils import log_errors


class ChatApp:
    def __init__(self, root):
        self.chat = None
        self.docs = None
        self.db = None
        self.file = None
        self.chat_history = []

        with open("config.json", "r") as f:
            self.config = json.load(f)

        self.root = root
        self.root.title("Chat with Ollama")
        self.root.geometry("1200x900")

        self.bg = "#181818"
        self.fg = "#EFEFEF"
        self.selected_bg = "#4A4A4A"
        self.selected_fg = "#ffffff"
        self.btn_bg = "#383838"
        self.warning_fg = "#ff6e91"

        self.main_frame = tk.Frame(master=self.root, width=1200, height=900, bg=self.bg)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.view_message_frame = tk.Frame(
            master=self.main_frame, width=1200, height=50, bg=self.bg
        )
        self.view_message_frame.pack(
            padx=5, pady=5, fill=tk.BOTH, side=tk.TOP, expand=True
        )

        self.send_message_frame = tk.Frame(
            master=self.main_frame, width=1200, height=50, bg=self.bg
        )
        self.send_message_frame.pack(padx=5, pady=5, fill=tk.X, side=tk.BOTTOM)

        self.notice_frame = tk.Frame(
            master=self.main_frame, width=1200, height=50, bg=self.btn_bg
        )
        self.notice_label = tk.Label(
            master=self.notice_frame,
            text="Choose a Model from the Options",
            bg=self.btn_bg,
            fg=self.warning_fg,
        )
        self.notice_frame.pack(
            padx=5,
            pady=5,
            fill=tk.X,
            side=tk.BOTTOM,
        )
        self.notice_label.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT)

        self.clear_btn = tk.Button(
            master=self.send_message_frame,
            text="Upload",
            command=self.upload_file,
            bg=self.btn_bg,
            fg=self.fg,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.clear_btn = tk.Button(
            master=self.send_message_frame,
            text="Clear",
            command=self.clear_conversation,
            bg=self.btn_bg,
            fg=self.fg,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.send_btn = tk.Button(
            master=self.send_message_frame,
            text="Send",
            command=self.send_message,
            bg=self.btn_bg,
            fg=self.fg,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
        )
        self.send_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.model_used_label = tk.Label(
            master=self.send_message_frame,
            text="Model: Empty",
            bg=self.bg,
            fg=self.fg,
            border=5,
        )
        self.model_used_label.pack(side=tk.RIGHT, padx=5, pady=5)

        self.user_input = tk.Entry(
            master=self.send_message_frame,
            width=50,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
            state=tk.DISABLED,
        )
        self.user_input.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.focus_set()

        self.menu = tk.Menu(
            self.root,
            tearoff=False,
            bg=self.btn_bg,
            fg=self.fg,
            relief=tk.FLAT,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
            activeborderwidth=0,
        )
        self.menu_item = tk.Menu(
            self.menu,
            tearoff=False,
            bg=self.btn_bg,
            fg=self.fg,
            relief=tk.FLAT,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
            activeborderwidth=0,
            postcommand=self.populate_model_menu,
        )

        self.model_menu = tk.Menu(
            self.menu_item,
            tearoff=False,
            bg=self.btn_bg,
            fg=self.fg,
            relief=tk.FLAT,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
            activeborderwidth=0,
        )

        self.menu.add_cascade(label="Options", menu=self.menu_item)
        self.menu_item.add_cascade(label="Chat Models", menu=self.model_menu)

        self.menu_item.add_command(label="Settings", command=self.settings)
        self.menu_item.add_command(label="Modelfile", command=self.modelfile)
        self.menu_item.add_command(label="Exit", command=self.exit_window)

        self.root.config(menu=self.menu)

        self.user_frame = None
        self.user_label = None
        self.response_frame = None
        self.response_label = None

        atexit.register(self.exit_window)
        signal.signal(signal.SIGINT, self.exit_on_signal)
        signal.signal(signal.SIGTERM, self.exit_on_signal)
        signal.signal(signal.SIGABRT, self.exit_on_signal)
        signal.signal(signal.SIGSEGV, self.exit_on_signal)
        signal.signal(signal.SIGBUS, self.exit_on_signal)
        signal.signal(signal.SIGFPE, self.exit_on_signal)
        signal.signal(signal.SIGILL, self.exit_on_signal)

    def send_message(self, event=None):
        user_prompt = str(self.user_input.get())
        self.user_input.delete(0, tk.END)
        self.chat_history.append(f"User: {user_prompt}")

        if self.file:
            if query_data:
                query_data = self.db.retrieval(user_prompt)
                generator = self.chat.chat_loop(
                    prompt=self.chat_history, file=self.file, query_data=query_data
                )
            else:
                generator = self.chat.chat_loop(
                    prompt=self.chat_history, file=self.file
                )
        else:
            generator = self.chat.chat_loop(self.chat_history)

        self.user_frame = tk.Frame(master=self.view_message_frame, bg=self.btn_bg)
        self.user_frame.pack(
            padx=5, pady=5, side=tk.BOTTOM, anchor=tk.E, before=self.response_frame
        )

        text_var = tk.StringVar()
        text_var.set(user_prompt)

        self.user_label = tk.Label(
            master=self.user_frame,
            textvariable=text_var,
            bg=self.btn_bg,
            fg=self.fg,
            wraplength=self.view_message_frame.winfo_width() * 0.6,
        )
        self.user_label.pack(side=tk.RIGHT)

        self.response_frame = tk.Frame(master=self.view_message_frame, bg=self.btn_bg)
        self.response_frame.pack(
            padx=5, pady=5, side=tk.BOTTOM, anchor=tk.W, before=self.user_frame
        )

        self.response_label = tk.Label(
            master=self.response_frame,
            bg=self.btn_bg,
            fg=self.fg,
            wraplength=self.view_message_frame.winfo_width() * 0.6,
        )
        self.response_label.pack(side=tk.LEFT, anchor=tk.W)

        self.stream_response(generator=generator)

    def stream_response(self, generator):
        try:
            response = next(generator)
            current_text = self.response_label.cget("text")
            new_text = current_text + response if current_text else response
            self.response_label.config(text=new_text)
            self.view_message_frame.after(100, self.stream_response, generator)
        except StopIteration:
            complete_message = str(self.response_label.cget("text"))
            self.chat_history.append(f"Assistant: {complete_message}")

    def populate_model_menu(self):
        all_models = display_models()
        chat_list = []

        for model in all_models:
            if model != "moondream":
                if "embed" not in model:
                    chat_list.append(model)

        chat_model_var = tk.StringVar()

        self.model_menu.delete(0, tk.END)

        for model in chat_list:
            self.model_menu.add_radiobutton(
                label=model,
                command=lambda m=model: self.update_chat_model(m),
                variable=chat_model_var,
                value=model,
            )

    def update_chat_model(self, model: str):
        self.clear_conversation()
        self.chat = OllamChat(model)
        self.model_used_label.config(text=f"Model: {model}")
        if self.user_input.cget("state") == tk.DISABLED:
            self.user_input.config(state=tk.NORMAL)
        notice = f"Now using model {model}"
        self.new_notice(notice=notice)

    def clear_conversation(self):
        for widget in self.view_message_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        self.chat_history = []

    def new_notice(self, notice: str):
        for widget in self.notice_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        new_notice_label = tk.Label(
            master=self.notice_frame,
            text=notice,
            bg=self.btn_bg,
            fg=self.fg,
        )
        new_notice_label.pack(padx=5, pady=5, fill=tk.BOTH, side=tk.LEFT)

    def upload_file(self):
        if self.chat:
            doc_path = "temp"
            if not os.path.exists(doc_path):
                os.makedirs(doc_path)

            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Files", ".txt .jpg .jpeg .png .bmp .gif"),
                ]
            )

            if file_path:
                if glob.glob(self.config["file"]):
                    os.remove(glob.glob(self.config["file"])[0])

                file_ext = os.path.splitext(file_path)[-1]
                file_name = file_path.split("/")[-1].split(".")[0]

                self.file = f"temp/temp{file_ext}"
                shutil.copy(file_path, self.file)

                img_ext = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]

                if file_ext not in img_ext:
                    self.docs = Documents(self.file, self.config["chunk_size"])
                    documents = self.docs.cleaning_process()
                    self.db = Database(self.config["db_path"], documents)
                    self.db.init_collection(self.file)
                    self.db.embedding()

                    notice = f"File {file_name} uploaded. Ready for query"
                    self.new_notice(notice=notice)
                else:
                    notice = f"Image {file_name} uploaded"
                    self.new_notice(notice=notice)
        else:
            notice = "Choose a chat model from options first!"
            self.new_notice(notice=notice)

    def settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")

        settings_frame = tk.Frame(
            master=settings_window, width=500, height=300, bg=self.bg
        )
        settings_frame.pack(fill=tk.BOTH, expand=True)

    def modelfile(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Modelfile")
        settings_window.geometry("500x300")

        settings_frame = tk.Frame(
            master=settings_window, width=500, height=300, bg=self.bg
        )
        settings_frame.pack(fill=tk.BOTH, expand=True)

    def exit_window(self):
        self.root.destroy()

    def exit_on_signal(self, sig, frame):
        self.root.destroy()
