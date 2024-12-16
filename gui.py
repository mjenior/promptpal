
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

from assistant import parse_arguments
from src.core import QueryManager
from src.api import OpenAIInterface



class RedirectStdoutToWidget:
    """
    Redirect standard output (stdout) to a given text widget.
    """

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.config(state="normal")
        self.text_widget.insert("end", text)
        self.text_widget.config(state="disabled")
        self.text_widget.see("end")  # Auto-scroll to the bottom

    def flush(self):
        pass  # Required for some compatibility with sys.stdout


class ChatGPTQueryApp:
    """
    A GUI application to assist novice users in crafting and submitting refined queries
    to ChatGPT with automated system role text.
    """

    def __init__(self, root):
        """
        Initialize the GUI components.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.root.title("ChatGPT Query Assistant")
        self.root.geometry("1200x500")

        # Initialize variables
        self.prompt = tk.StringVar()
        self.instructions = tk.StringVar()
        self.role = tk.StringVar(value="assistant")
        self.model = tk.StringVar(value="gpt-4o-mini")
        self.chain_of_thought = tk.BooleanVar(value=False) 
        self.reflection = tk.BooleanVar(value=False) 
        self.code = tk.BooleanVar(value=False) 
        self.log = tk.BooleanVar(value=False) 
        self.iterations = tk.IntVar(value=1)
        self.output_text = tk.StringVar()

        # Create GUI Layout
        self.create_widgets()


    def create_widgets(self):
        """Create and arrange all GUI components."""
        # Left Panel: Input Fields
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Main text entry
        ttk.Label(left_frame, text="User Prompt:").grid(row=0, column=0, sticky="w")
        self.prompt = tk.Text(left_frame, height=5, wrap=tk.WORD)
        self.prompt.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        ttk.Label(left_frame, text="Additional System Instructions:").grid(row=2, column=0, sticky="w")
        self.instructions = tk.Text(left_frame, height=5, wrap=tk.WORD)
        self.instructions.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        # Dropdown Menus
        ttk.Label(left_frame, text="System Role").grid(row=4, column=0, sticky="w")
        self.role.set("assistant")
        ttk.OptionMenu(left_frame, self.role, "assistant", "Option 2", "Option 3").grid(
            row=5, column=0, sticky="ew", padx=5, pady=2
        )
        ttk.Label(left_frame, text="Model:").grid(row=6, column=0, sticky="w")
        self.model.set("gpt-4o-mini")
        ttk.OptionMenu(left_frame, self.model, "gpt-4o-mini", "Option B", "Option C").grid(
            row=7, column=0, sticky="ew", padx=5, pady=2
        )

        # Boolean Switches
        switch_frame = ttk.Frame(left_frame)
        switch_frame.grid(row=8, column=0, sticky="ew", padx=5, pady=10)
        ttk.Checkbutton(switch_frame, text=f"Chain of Thought prompting", variable=self.chain_of_thought
                        ).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(switch_frame, text=f"Context Reflection", variable=self.reflection
                        ).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(switch_frame, text=f"Save code separately", variable=self.code
                        ).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(switch_frame, text=f"Save conversation log", variable=self.log
                        ).grid(row=2, column=0, sticky="w")

        # Other
        ttk.Label(left_frame, text="Response Iterations:").grid(row=9, column=0, sticky="w")
        ttk.Entry(left_frame, textvariable=self.iterations).grid(
            row=10, column=0, sticky="ew", padx=5, pady=5
        )

        # Submit Button
        ttk.Button(left_frame, text="Submit", command=self.submit_query).grid(
            row=12, column=0, sticky="ew", padx=5, pady=10)

        # Right Panel: Output Field
        self.stdout_redirector = RedirectStdoutToWidget(self.create_output_field())
        self.stdout_redirector = sys.stdout


    def create_output_field(self):
        """Create the output field for displaying results and redirecting stdout."""
        # Right Panel: Output Field
        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right_frame, text="Output:").grid(row=0, column=0, sticky="w")
        output_display = tk.Text(right_frame, height=40, wrap=tk.WORD, state="disabled")
        output_display.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Expandability
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)

        return output_display
    

    def submit_query(self):
        """
        Process the user input, generate a response, and display the output.

        This simulates interaction with ChatGPT using the collected data.
        """
        # Get input
        args = parse_arguments()
        args.prompt = self.prompt.get("1.0", tk.END).strip()
        instructions = self.instructions.get("1.0", tk.END).strip()
        print(self.role)
        args.role = self.role.get().strip()
        args.model = self.model.get().strip()
        args.chain_of_thought = self.chain_of_thought.get()
        args.reflection = self.reflection.get()
        args.code = self.code.get()
        args.log = self.log.get()

        # Initialize the user argument and query manager
        io_manager = QueryManager(args)
        # Initialize the OpenAI API handler and submit query
        api_handler = OpenAIInterface(io_manager)
        api_handler.submit_query(io_manager)


if __name__ == "__main__":
    # Initialize the application
    root = tk.Tk()
    app = ChatGPTQueryApp(root)
    root.mainloop()
