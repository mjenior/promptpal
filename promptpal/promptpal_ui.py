import ipywidgets as widgets
from IPython.display import display

from .promptpal import Promptpal


class PromptpalUI:
    def __init__(self):
        self.promptpal = Promptpal()

        self.refine_method_select = widgets.RadioButtons(
            options=[
                "Prompt Engineer",
                "Prompt Refiner Agent",
                "Chain of Thought",
                "Keyword Refinement",
                "Glyph Refinement",
            ],
            layout=widgets.Layout(width="200px", height="150px"),
        )

        self.tool_output = widgets.Textarea(layout=widgets.Layout(width="800px", height="150px"))

        self.refine_button = widgets.Button(
            description="Refine Prompt", layout=widgets.Layout(width="250px")
        )

        self.refine_button.on_click(self.refine_prompt)

        self.update_prompt_button = widgets.Button(
            description="Update Prompt", layout=widgets.Layout(width="250px")
        )

        self.update_prompt_button.on_click(self.update_prompt)

        self.get_advice_button = widgets.Button(
            description="Get Advice", layout=widgets.Layout(width="250px")
        )

        self.get_advice_button.on_click(self.get_advice)

        self.clear_button = widgets.Button(
            description="Clear", layout=widgets.Layout(width="250px")
        )

        self.clear_button.on_click(self.clear)

        self.prompt_input = widgets.Textarea(
            value="",
            placeholder="Enter your prompt here",
            layout=widgets.Layout(width="500px", height="500px"),
        )

        self.refined_prompt_output = widgets.Textarea(
            placeholder="Refined prompt will appear here",
            layout=widgets.Layout(width="500px", height="500px"),
        )

        self.layout = widgets.Box(
            (
                widgets.VBox(
                    (
                        widgets.HBox(
                            (
                                widgets.VBox(
                                    (
                                        widgets.Label("Refinement Method"),
                                        self.refine_method_select,
                                    )
                                ),
                                self.tool_output,
                            )
                        ),
                        widgets.HBox(
                            (
                                self.refine_button,
                                self.update_prompt_button,
                                self.get_advice_button,
                                self.clear_button,
                            )
                        ),
                        widgets.HBox(
                            (
                                widgets.VBox(
                                    (
                                        widgets.Label("Prompt"),
                                        self.prompt_input,
                                    )
                                ),
                                widgets.VBox(
                                    (
                                        widgets.Label("Refined Prompt"),
                                        self.refined_prompt_output,
                                    )
                                ),
                            )
                        ),
                    )
                ),
            )
        )

        display(self.layout)

    def refine_prompt(self, button):
        self.tool_output.value = "Refining prompt..."

        refine_method = self.refine_method_select.value
        current_prompt = self.prompt.value

        self.refined_prompt_output.value = "Prompt that has been refined. "

        self.tool_output.value = "Prompt refined using " + refine_method

    def update_prompt(self, button):
        self.tool_output.value = "Updated prompt"

    def get_advice(self, button):
        self.tool_output.value = "Advice on prompt"

    def clear(self, button):
        self.tool_output.value = ""
        self.prompt.value = ""
        self.refined_prompt_output.value = ""
