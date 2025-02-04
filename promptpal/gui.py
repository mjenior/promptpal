#!/usr/bin/env python3

import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk

from core import CreateAgent  # Assuming core.py is in the same directory


class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenAI Agent Interface")
        self.root.geometry("800x600")
        
        # Input panel
        self.frame_input = tk.Frame(self.root)
        self.frame_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Output panel
        self.frame_output = tk.Frame(self.root)
        self.frame_output.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Creating input fields and checkboxes
        self.verbose_var = tk.BooleanVar()
        self.silent_var = tk.BooleanVar()
        
        tk.Checkbutton(self.frame_input, text="Verbose Logging", variable=self.verbose_var).pack(anchor='w')
        tk.Checkbutton(self.frame_input, text="Silent Mode", variable=self.silent_var).pack(anchor='w')
        
        self.model_label = tk.Label(self.frame_input, text="Model:")
        self.model_label.pack()
        self.model_entry = tk.Entry(self.frame_input)
        self.model_entry.pack()

        self.role_label = tk.Label(self.frame_input, text="Role:")
        self.role_label.pack()
        self.role_entry = tk.Entry(self.frame_input)
        self.role_entry.pack()

        self.prompt_label = tk.Label(self.frame_input, text="Prompt:")
        self.prompt_label.pack()
        self.prompt_entry = tk.Text(self.frame_input, height=5, width=40)
        self.prompt_entry.pack()

        self.submit_button = tk.Button(self.frame_input, text="Send Request", command=self.send_request)
        self.submit_button.pack()

        # Output scrolled text area
        self.output_area = scrolledtext.ScrolledText(self.frame_output, wrap=tk.WORD)
        self.output_area.pack(expand=True, fill='both')

    def collect_input(self):
        """Collect inputs from the GUI."""
        inputs = {
            'verbose': self.verbose_var.get(),
            'silent': self.silent_var.get(),
            'model': self.model_entry.get() or "gpt-4o-mini",
            'role': self.role_entry.get() or "assistant",
            'prompt': self.prompt_entry.get("1.0", tk.END).strip(),
            # Add any other attributes as needed
        }
        return inputs

    def send_request(self):
        """Handle API request in a separate thread to keep the UI responsive."""
        inputs = self.collect_input()
        thread = threading.Thread(target=self.make_api_request, args=(inputs,))
        thread.start()

    def make_api_request(self, inputs):
        """Make a request to the OpenAI API and display the result."""
        try:
            agent = CreateAgent(logging=inputs['verbose'], 
                                silent=inputs['silent'], 
                                model=inputs['model'], 
                                role=inputs['role'])
            response = agent.request(prompt=inputs['prompt'])
            self.output_area.insert(tk.END, response + "\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    gui = AgentGUI(root)
    root.mainloop()