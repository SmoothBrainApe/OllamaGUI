import tkinter as tk
from tkinter import filedialog
import signal
import shutil
import os
import json
import glob
from PIL import Image, ImageTk
from backend.chat import OllamaChat
from backend.database import Database
from backend.docs_process import Documents
from backend.utils import (
    display_models,
    display_modelfile,
    create_modelfile,
    get_system_prompt,
    get_template,
    split_modelfile,
    parse_parameters,
    pull_model,
    logging,
)


class ChatApp:
    def __init__(self, root):
        self.chat = None
        self.docs = None
        self.db = None
        self.file = None
        self.chat_history = []

        if not os.path.exists("config.json"):
            with open("config.json", "w") as f:
                default_config = {
                    "db_path": "database",
                    "file": "temp/*",
                    "chunk_size": 50,
                }
                json.dump(default_config, f)

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

        self.upload_btn = self.create_button(
            master=self.send_message_frame,
            text="Upload",
            command=self.upload_file,
        )
        self.upload_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.clear_btn = self.create_button(
            master=self.send_message_frame,
            text="Clear",
            command=self.clear_conversation,
        )
        self.clear_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        self.send_btn = self.create_button(
            master=self.send_message_frame,
            text="Send",
            command=self.send_message,
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

        self.menu_item.add_command(label="Pull Model", command=self.pull_model_window)
        self.menu_item.add_command(label="Settings", command=self.settings)
        self.menu_item.add_command(label="Exit", command=self.exit_window)

        self.root.config(menu=self.menu)

        self.user_frame = None
        self.user_label = None
        self.response_frame = None
        self.response_label = None
        self.unload_btn = None
        self.pull_window = None
        self.pull_entry = None

        self.chat_list = []
        self.embed_list = []
        self.vision_list = []

        self.embed_list_frame = None
        self.embed_model = "nomic-text-embed"
        self.vision_list_frame = None
        self.vision_model = "moondream"
        self.chunk_size_entry = None
        self.modelfile_current_frame = None
        self.settings_frame = None
        self.modelfil_frame = None
        self.temp_entry = None
        self.topk_entry = None
        self.topp_entry = None
        self.ctx_entry = None
        self.gpu_entry = None
        self.stop_entry = None
        self.stop_listbox = None
        self.template_textbox = None
        self.system_textbox = None

        self.root.protocol("WM_DELETE_WINDOW", self.exit_window)
        signal.signal(signal.SIGINT, self.exit_on_signal)
        signal.signal(signal.SIGTERM, self.exit_on_signal)
        signal.signal(signal.SIGABRT, self.exit_on_signal)

    def send_message(self, event=None):
        user_prompt = str(self.user_input.get())
        print(event)
        self.user_input.delete(0, tk.END)
        self.chat_history.append(f"User: {user_prompt}")

        if self.file:
            img_ext = ["png", "jpg", "jpeg", "bmp", "gif"]
            file_ext = self.file.split("/")[-1].split(".")[-1]
            if file_ext not in img_ext:
                if len(self.chat_history) == 1:
                    query_data = self.db.retrieval(user_prompt)
                else:
                    modified_query = self.chat.history_aware_query(self.chat_history)
                    query_data = self.db.retrieval(modified_query)
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

    def pull_model_window(self):
        self.pull_window = tk.Toplevel(self.root)
        self.pull_window.title("Pull Model")

        pull_frame = tk.Frame(master=self.pull_window, bg=self.bg)
        pull_frame.pack(fill=tk.BOTH, expand=True)

        pull_label = tk.Label(
            master=pull_frame,
            text="Enter the Model you wish to pull:",
            bg=self.bg,
            fg=self.fg,
        )
        self.pull_entry = tk.Entry(
            master=pull_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        pull_button = self.create_button(
            master=pull_frame, text="Pull Model", command=self.pull_button
        )

        pull_label.pack(side=tk.TOP, padx=5, pady=5)
        self.pull_entry.pack(side=tk.TOP, padx=5, pady=5)
        pull_button.pack(side=tk.TOP, padx=5, pady=5)

    def pull_button(self):
        model = self.pull_entry.get()
        self.pull_window.destroy()
        pull_model(str(model))

    def populate_model_menu(self):
        all_models = display_models()

        for model in all_models:
            if model != "moondream":
                if "llava" not in model:
                    if "embed" not in model:
                        self.chat_list.append(model)
                    else:
                        self.embed_list.append(model)
                else:
                    self.vision_list.append(model)
            else:
                self.vision_list.append(model)

        if not self.chat_list:
            notice = "There are no models for chat. Please pull a model from Ollama."
            self.new_notice(notice=notice)

        chat_model_var = tk.StringVar()

        self.model_menu.delete(0, tk.END)

        for model in self.chat_list:
            self.model_menu.add_radiobutton(
                label=model,
                command=lambda m=model: self.update_chat_model(m),
                variable=chat_model_var,
                value=model,
            )

    def update_chat_model(self, model: str):
        self.clear_conversation()
        self.chat = OllamaChat(model, self.vision_model)
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
                    self.db = Database(
                        self.config["db_path"], documents, self.embed_model
                    )
                    self.db.init_collection(self.file)
                    self.db.embedding()

                    notice = f"File {file_name} uploaded. Ready for query"
                    self.new_notice(notice=notice)
                else:
                    self.user_frame = tk.Frame(
                        master=self.view_message_frame, bg=self.btn_bg
                    )
                    self.user_frame.pack(
                        padx=5,
                        pady=5,
                        side=tk.BOTTOM,
                        anchor=tk.E,
                        before=self.response_frame,
                    )

                    pil_image = Image.open(self.file)
                    image_size = (400, 400)
                    pil_image.thumbnail(image_size)
                    tk_image = ImageTk.PhotoImage(pil_image)
                    self.user_label = tk.Label(
                        master=self.user_frame,
                        image=tk_image,
                        bg=self.btn_bg,
                        fg=self.fg,
                        wraplength=self.view_message_frame.winfo_width() * 0.6,
                    )
                    self.user_label.image = tk_image
                    self.user_label.pack(side=tk.RIGHT)

                    notice = f"Image {file_name} uploaded"
                    self.new_notice(notice=notice)

                self.unload_btn = self.create_button(
                    master=self.send_message_frame,
                    text="Remove File",
                    command=self.remove_file,
                )
                self.unload_btn.pack(
                    side=tk.RIGHT, padx=5, pady=5, before=self.upload_btn
                )
        else:
            notice = "Choose a chat model from options first!"
            self.new_notice(notice=notice)

    def remove_file(self):
        file = glob.glob("temp/*")
        if file:
            os.remove(file[0])

        self.unload_btn.destroy()
        notice = "File removed"
        self.new_notice(notice=notice)

    def create_button(self, master, text, command):
        return tk.Button(
            master=master,
            text=text,
            command=command,
            bg=self.btn_bg,
            fg=self.fg,
            border=0,
            activebackground=self.selected_bg,
            activeforeground=self.selected_fg,
        )

    def settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("1000x800")

        current_modelfile, model_name = self.parse_modelfile()
        if current_modelfile:
            source, param, template, system = split_modelfile(
                modelfile=current_modelfile
            )
        else:
            param = None
            template = None
            system = None

        button_frame = tk.Frame(
            master=settings_window, width=1000, height=50, bg=self.btn_bg
        )
        button_frame.pack(side=tk.TOP, fill=tk.X)

        self.settings_frame = tk.Frame(
            master=settings_window, height=550, width=1000, bg=self.bg
        )
        self.settings_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)

        general_settings_frame = tk.Frame(
            master=self.settings_frame,
            bg=self.bg,
            highlightbackground=self.fg,
            highlightthickness=2,
        )
        self.embed_list_frame = tk.Frame(
            master=self.settings_frame,
            bg=self.bg,
            highlightbackground=self.fg,
            highlightthickness=2,
        )
        self.vision_list_frame = tk.Frame(
            master=self.settings_frame,
            bg=self.bg,
            highlightbackground=self.fg,
            highlightthickness=2,
        )

        general_settings_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.embed_list_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        self.vision_list_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        chunk_size_label = tk.Label(
            master=general_settings_frame, text="Chunk Size", bg=self.bg, fg=self.fg
        )
        self.chunk_size_entry = tk.Entry(
            master=general_settings_frame,
            width=10,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        save_btn = self.create_button(
            master=general_settings_frame, text="Save", command=self.save_settings
        )
        chunk_size_label.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        self.chunk_size_entry.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        save_btn.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)

        chunk_size = self.config["chunk_size"]
        if chunk_size:
            self.chunk_size_entry.insert(tk.END, chunk_size)

        self.modelfile_frame = tk.Frame(
            master=settings_window, height=550, width=1000, bg=self.bg
        )
        parameter_frame = tk.Frame(
            master=self.modelfile_frame,
            bg=self.bg,
            height=200,
            highlightbackground=self.fg,
            highlightthickness=2,
        )
        template_frame = tk.Frame(
            master=self.modelfile_frame,
            bg=self.bg,
            highlightbackground=self.fg,
            highlightthickness=2,
        )
        system_frame = tk.Frame(
            master=self.modelfile_frame,
            bg=self.bg,
            highlightbackground=self.fg,
            highlightthickness=2,
        )
        parameter_frame.pack(fill=tk.X, side=tk.TOP)
        template_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        system_frame.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)

        temp_label = tk.Label(
            master=parameter_frame, text="Temperature", bg=self.bg, fg=self.fg
        )
        self.temp_entry = tk.Entry(
            master=parameter_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        topk_label = tk.Label(
            master=parameter_frame, text="Top_k", bg=self.bg, fg=self.fg
        )
        self.topk_entry = tk.Entry(
            master=parameter_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        topp_label = tk.Label(
            master=parameter_frame, text="Top_p", bg=self.bg, fg=self.fg
        )
        self.topp_entry = tk.Entry(
            master=parameter_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        ctx_label = tk.Label(
            master=parameter_frame, text="num_ctx", bg=self.bg, fg=self.fg
        )
        self.ctx_entry = tk.Entry(
            master=parameter_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        gpu_label = tk.Label(
            master=parameter_frame, text="num_gpu", bg=self.bg, fg=self.fg
        )
        self.gpu_entry = tk.Entry(
            master=parameter_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        stop_label = tk.Label(
            master=parameter_frame, text="stop", bg=self.bg, fg=self.fg
        )
        self.stop_listbox = tk.Listbox(
            master=parameter_frame, bg=self.btn_bg, fg=self.fg
        )
        self.stop_entry = tk.Entry(
            master=parameter_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        add_stop_btn = self.create_button(
            master=parameter_frame, text="+", command=self.add_stop
        )
        remove_stop_btn = self.create_button(
            master=parameter_frame, text="-", command=self.remove_stop
        )

        temp_label.grid(row=0, column=0, padx=5, pady=5)
        self.temp_entry.grid(row=0, column=1, padx=5, pady=5)
        topk_label.grid(row=1, column=0, padx=5, pady=5)
        self.topk_entry.grid(row=1, column=1, padx=5, pady=5)
        topp_label.grid(row=2, column=0, padx=5, pady=5)
        self.topp_entry.grid(row=2, column=1, padx=5, pady=5)
        ctx_label.grid(row=3, column=0, padx=5, pady=5)
        self.ctx_entry.grid(row=3, column=1, padx=5, pady=5)
        gpu_label.grid(row=4, column=0, padx=5, pady=5)
        self.gpu_entry.grid(row=4, column=1, padx=5, pady=5)
        stop_label.grid(row=0, column=3, padx=5, pady=5)
        self.stop_entry.grid(row=0, column=4, padx=5, pady=5)
        self.stop_listbox.grid(row=1, column=4, columnspan=3, rowspan=4, padx=5, pady=5)
        add_stop_btn.grid(row=2, column=3, padx=5, pady=5)
        remove_stop_btn.grid(row=3, column=3, padx=5, pady=5)

        if param:
            temp, topk, topp, ctx, gpu, stop = parse_parameters(param)
        else:
            temp = None
            topk = None
            topp = None
            ctx = None
            gpu = None
            stop = []

        if temp:
            self.insert_value(self.temp_entry, temp)
        if topk:
            self.insert_value(self.topk_entry, topk)
        if topp:
            self.insert_value(self.topp_entry, topp)
        if ctx:
            self.insert_value(self.ctx_entry, ctx)
        if gpu:
            self.insert_value(self.gpu_entry, gpu)
        if stop:
            for s in stop:
                self.insert_value(self.stop_listbox, s)

        template_label = tk.Label(
            master=template_frame, text="Template", bg=self.bg, fg=self.fg
        )
        template_label.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        self.template_textbox = tk.Text(
            master=template_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        self.template_textbox.pack(
            fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=10, pady=10
        )

        if model_name:
            template_label.config(text=f"Template: {model_name}")
        if template:
            template_prompt = get_template(template=template)
            if template_prompt:
                self.template_textbox.insert(
                    tk.END,
                    template_prompt,
                )

        system_label = tk.Label(
            master=system_frame, text="System Prompt", bg=self.bg, fg=self.fg
        )
        system_label.pack(side=tk.TOP, anchor=tk.W, padx=10, pady=10)
        system_btn = self.create_button(
            master=system_frame, text="Save", command=self.save_modelfile
        )
        system_btn.pack(side=tk.BOTTOM, anchor=tk.E, padx=10, pady=10)
        self.system_textbox = tk.Text(
            master=system_frame,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        self.system_textbox.pack(
            fill=tk.BOTH, side=tk.RIGHT, expand=True, padx=10, pady=10
        )

        if model_name:
            system_label.config(text=f"System Prompt: {model_name}")
        if system:
            system_prompt = get_system_prompt(system=system)
            if system_prompt:
                self.system_textbox.insert(
                    tk.END,
                    system_prompt,
                )

        settings_button = self.create_button(
            master=button_frame,
            text="General Settings",
            command=self.show_settings,
        )
        settings_button.pack(side=tk.LEFT, padx=5, pady=5)
        modelfile_button = self.create_button(
            master=button_frame,
            text="Modelfile Settings",
            command=self.show_modelfile,
        )
        modelfile_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.modelfile_current_frame = self.settings_frame
        self.populate_models_in_settings()

    def parse_modelfile(self) -> str:
        current_model = self.model_used_label.cget("text")
        model_name = current_model.split(" ")[-1].strip()
        if model_name == "Empty":
            return None, None
        else:
            return display_modelfile(model_name), model_name

    def save_modelfile(self):
        current_modelfile, model_name = self.parse_modelfile()
        source, param, template, system = split_modelfile(modelfile=current_modelfile)
        stops = ""

        saved_temp = self.temp_entry.get()
        if saved_temp:
            temp = "PARAMETER temperature " + saved_temp
        saved_topk = self.topk_entry.get()
        if saved_topk:
            topk = "PARAMETER top_k " + saved_topk
        saved_topp = self.topp_entry.get()
        if saved_topp:
            topp = "PARAMETER top_p " + saved_topp
        saved_ctx = self.ctx_entry.get()
        if saved_ctx:
            ctx = "PARAMETER num_ctx " + saved_ctx
        saved_gpu = self.gpu_entry.get()
        if saved_gpu:
            gpu = "PARAMETER num_gpu " + saved_gpu
        saved_stops = self.stop_listbox.get(0, tk.END)
        if saved_stops:
            for stop in saved_stops:
                stops += "PARAMETER stop " + stop + "\n"

        if temp or topk or topp or ctx or gpu or stops:
            param = "\n".join(
                [value for value in [temp, topk, topp, ctx, gpu, stops] if value]
            ).strip()

        saved_system = self.system_textbox.get("1.0", tk.END)
        if saved_system:
            system = 'SYSTEM """\n' + saved_system + '"""'

        saved_template = self.template_textbox.get("1.0", tk.END)
        if saved_template:
            template = 'TEMPLATE """\n' + saved_template + '"""'

        new_modelfile = source + "\n\n" + param + "\n\n" + template + "\n\n" + system
        notice = create_modelfile(model_name, new_modelfile)
        print(notice)

    def insert_value(self, widget, value):
        widget.delete(0, tk.END)
        value = value.split()[-1]
        widget.insert(tk.END, value)

    def add_stop(self):
        entry = self.stop_entry.get()
        if entry:
            self.stop_listbox.insert(tk.END, entry)
            self.stop_entry.delete(0, tk.END)

    def remove_stop(self):
        selected_index = self.stop_listbox.curselection()
        if selected_index:
            self.stop_listbox.delete(selected_index)

    def save_settings(self):
        self.config["chunk_size"] = int(self.chunk_size_entry.get())

        if not os.path.exists("config.json"):
            with open("config.json", "w") as f:
                json.dump(self.config, f)

    def populate_models_in_settings(self):
        if self.embed_list_frame.winfo_children():
            for widget in self.embed_list_frame.winfo_children():
                widget.destroy()

        if self.vision_list_frame.winfo_children():
            for widget in self.vision_list_frame.winfo_children():
                widget.destroy()

        if not self.embed_list:
            no_embed_model_label = tk.Label(
                master=self.vision_list_frame,
                text="No Embed Model Available",
                bg=self.bg,
                fg=self.fg,
            )
            no_embed_model_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        else:
            embed_model_label = tk.Label(
                master=self.embed_list_frame,
                text="Choose Embed Models",
                bg=self.bg,
                fg=self.fg,
            )
            embed_model_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
            embed_model_var = tk.StringVar()
            for model in self.embed_list:
                embed_model_opt = tk.Radiobutton(
                    master=self.embed_list_frame,
                    text=str(model),
                    bg=self.bg,
                    fg=self.fg,
                    activebackground=self.selected_bg,
                    activeforeground=self.selected_fg,
                    variable=embed_model_var,
                    value=str(model),
                    selectcolor="black",
                    command=lambda m=model: self.choose_embed_model(m),
                )
                embed_model_opt.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)

        if not self.vision_list:
            no_vision_model_label = tk.Label(
                master=self.vision_list_frame,
                text="No Vision Model Available",
                bg=self.bg,
                fg=self.fg,
            )
            no_vision_model_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        else:
            vision_model_label = tk.Label(
                master=self.vision_list_frame,
                text="Choose Vision Models",
                bg=self.bg,
                fg=self.fg,
            )
            vision_model_label.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
            vision_model_var = tk.StringVar()
            for model in self.vision_list:
                vision_model_opt = tk.Radiobutton(
                    master=self.vision_list_frame,
                    text=str(model),
                    bg=self.bg,
                    fg=self.fg,
                    activebackground=self.selected_bg,
                    activeforeground=self.selected_fg,
                    variable=vision_model_var,
                    value=str(model),
                    selectcolor="black",
                    command=lambda m=model: self.choose_vision_model(m),
                )
                vision_model_opt.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)

    def choose_embed_model(self, model):
        self.embed_model = model
        print(model)

    def choose_vision_model(self, model):
        self.vision_model = model
        print(model)

    def switch_frame(self, new_frame):
        if self.modelfile_current_frame != new_frame:
            self.modelfile_current_frame.pack_forget()
            new_frame.pack(fill=tk.BOTH, side=tk.BOTTOM, expand=True)
            self.modelfile_current_frame = new_frame

    def show_settings(self):
        self.switch_frame(self.settings_frame)
        self.populate_models_in_settings()

    def show_modelfile(self):
        self.switch_frame(self.modelfile_frame)

    def exit_function(self):
        if glob.glob(self.config["file"]):
            file = glob.glob(self.config["file"])[0]

            if os.path.exists(file):
                os.remove(file)

        if os.path.exists(self.config["db_path"]):
            shutil.rmtree(self.config["db_path"])
        self.root.destroy()

    def exit_window(self):
        self.exit_function()

    def exit_on_signal(self, sig, frame):
        self.exit_function()
