import tkinter as tk
from tkinter import ttk
from rsa_frame import rsa_frame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PGP")
        self.geometry("600x600")

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        frames = [rsa_frame(notebook)]
        for frame in frames:
            notebook.add(frame, text=frame.title)


if __name__ == "__main__":
    app = App()
    app.mainloop()