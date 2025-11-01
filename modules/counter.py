from tkinter import Tk, Label, Button, font, Frame

class Counter(Tk):
    """A simple counter GUI application."""
    def __init__(self, word: str, screenName: str | None = None, baseName: str | None = None, className: str = "Tk", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        """Initialize the counter GUI."""

        self.count = 0
        self.font = font.Font(family="Helvetica", size=20)

        self.title("The " + word + " Counter")
        self.attributes('-topmost', True)
        self.geometry("300x200")
        self.minsize(300, 200)
        
        frame = Frame(self)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure([0, 1, 2], weight=1)

        self.counter_label = Label(frame, text="0", font=self.font)
        self.counter_label.grid(column=0, row=1, sticky="nsew")

        Label(frame, text=("The " + word + " Counter"), font=self.font).grid(column=0, row=0, sticky="nsew")
        Button(frame, text=("+1 " + word), command = self.increment, font=self.font).grid(column=0, row=2, sticky="nsew")

    def increment(self):
        """Increment the counter by 1."""
        self.count += 1
        self.counter_label.config(text=str(self.count))


def do_counter(self, args):
    """Open a simple counter GUI. Usage: counter [word]"""
    app = Counter(word=args if args else "Anything")
    
    app.mainloop()
