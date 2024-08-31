import tkinter as tk
import signal
import atexit
from backend.chat import OllamChat


class ChatApp:
    def __init__(self, root):
        # self.root = tk.Tk()
        self.chat = OllamChat("Test")
        self.chat_history = []

        self.root = root
        self.root.title("Chat with Ollama")
        self.root.geometry("1600x900")

        self.bg = "#181818"
        self.fg = "#EFEFEF"
        self.selected_bg = "#4A4A4A"
        self.selected_fg = "#ffffff"
        self.btn_bg = "#383838"

        self.main_frame = tk.Frame(master=self.root, width=1600, height=900, bg=self.bg)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.view_message_frame = tk.Frame(
            master=self.main_frame, width=50, height=50, bg=self.bg
        )
        self.view_message_frame.pack(
            padx=5, pady=5, fill=tk.BOTH, side=tk.TOP, expand=True
        )

        self.send_message_frame = tk.Frame(
            master=self.main_frame, width=50, height=50, bg=self.bg
        )
        self.send_message_frame.pack(padx=5, pady=5, fill=tk.X, side=tk.BOTTOM)

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

        self.user_input = tk.Entry(
            master=self.send_message_frame,
            width=50,
            bg=self.btn_bg,
            fg=self.fg,
            insertbackground=self.fg,
        )
        self.user_input.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.user_input.bind("<Return>", self.send_message)
        self.user_input.focus_set()

        self.menu = tk.Menu(
            self.root,
            tearoff=False,
            bg=self.bg,
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
        )

        self.user_frame = None
        self.user_label = None
        self.response_frame = None
        self.response_label = None

        self.menu_item.add_command(label="Settings", command=self.settings)
        self.menu_item.add_command(label="Exit", command=self.exit_window)

        self.root.protocol("WM_DELETE_WINDOW", self.exit_window)
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
        self.chat_history.append(f"User: {user_prompt}")
        self.user_input.delete(0, tk.END)
        generator = self.chat.simple_chat(self.chat_history)
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

    def clear_conversation(self):
        for widget in self.view_message_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()

    def settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x300")

    def exit_window(self):
        self.root.destroy()

    def exit_on_signal(self, sig, frame):
        self.root.destroy()
