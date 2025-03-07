import ipywidgets as widgets
from IPython.display import display

from .promptpal import Promptpal, PromptRefinementType


class PromptpalUI:
    def __init__(self, vertexai: bool = True, project: str = "", location: str = ""):
        self.promptpal = Promptpal(vertexai=vertexai, project=project, location=location)

        self.refine_method_select = widgets.RadioButtons(
            options=[
                "Prompt Engineer",
                "Prompt Refiner Agent",
                "Chain of Thought",
                "Chain of Draft",
                "Keyword Refinement",
                "Glyph Refinement",
            ],
            layout=widgets.Layout(width="200px", height="150px"),
        )

        self.tool_output = widgets.Textarea(layout=widgets.Layout(width="400px", height="150px"))

        self.refine_button = widgets.Button(description="Refine Prompt", layout=widgets.Layout(width="150px"))

        self.refine_button.on_click(self.refine_prompt)

        self.update_prompt_button = widgets.Button(description="Update Prompt", layout=widgets.Layout(width="150px"))

        self.update_prompt_button.on_click(self.update_prompt)

        self.get_advice_button = widgets.Button(description="Get Advice", layout=widgets.Layout(width="150px"))

        self.get_advice_button.on_click(self.get_advice)

        self.clear_button = widgets.Button(description="Clear", layout=widgets.Layout(width="150px"))

        self.clear_button.on_click(self.clear)

        self.prompt_input = widgets.Textarea(
            value="",
            placeholder="Enter your prompt here",
            layout=widgets.Layout(width="300px", height="400px"),
        )

        self.refined_prompt_output = widgets.Textarea(
            placeholder="Refined prompt will appear here",
            layout=widgets.Layout(width="300px", height="400px"),
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

    def _get_refinement_type(self, method_name):
        """Convert UI method name to PromptRefinementType enum value."""
        method_mapping = {
            "Prompt Engineer": PromptRefinementType.PROMPT_ENGINEER,
            "Prompt Refiner Agent": PromptRefinementType.REFINE_PROMPT,
            "Chain of Thought": PromptRefinementType.CHAIN_OF_THOUGHT,
            "Keyword Refinement": PromptRefinementType.KEYWORD,
            "Glyph Refinement": PromptRefinementType.GLYPH,
        }
        return method_mapping.get(method_name)

    def refine_prompt(self, button):
        """Refine the current prompt using the selected refinement method."""
        self.tool_output.value = "Refining prompt..."

        # Get the selected refinement method and current prompt
        refine_method = self.refine_method_select.value
        current_prompt = self.prompt_input.value

        if not current_prompt:
            self.tool_output.value = "Error: Please enter a prompt to refine."
            return

        try:
            # Convert UI method name to PromptRefinementType enum
            refinement_type = self._get_refinement_type(refine_method)

            if refinement_type is None:
                self.tool_output.value = f"Error: Unknown refinement method '{refine_method}'."
                return

            # Call the Promptpal refine_prompt method
            refined_prompt = self.promptpal.refine_prompt(current_prompt, refinement_type)

            # Update the refined prompt output
            self.refined_prompt_output.value = refined_prompt

            # Update the tool output
            self.tool_output.value = f"Prompt refined using {refine_method}."

        except Exception as e:
            self.tool_output.value = f"Error refining prompt: {e!s}"

    def update_prompt(self, button):
        """Update the current prompt with the refined prompt."""
        refined_prompt = self.refined_prompt_output.value

        if not refined_prompt:
            self.tool_output.value = "Error: No refined prompt to update with."
            return

        # Update the current prompt with the refined prompt
        self.prompt_input.value = refined_prompt

        # Clear the refined prompt output
        self.refined_prompt_output.value = ""

        # Update the tool output
        self.tool_output.value = "Current prompt updated with refined prompt."

    def get_advice(self, button):
        """Get advice on the current prompt from the prompt_advisor role."""
        current_prompt = self.prompt_input.value

        if not current_prompt:
            self.tool_output.value = "Error: Please enter a prompt to get advice on."
            return

        try:
            # Call the prompt_advisor role
            self.tool_output.value = "Getting advice on prompt..."
            advice = self.promptpal.message("prompt_advisor", f"Analyze this prompt: {current_prompt}")

            # Update the tool output with the advice
            self.tool_output.value = advice

        except Exception as e:
            self.tool_output.value = f"Error getting advice: {e!s}"

    def clear(self, button):
        """Clear all inputs and outputs."""
        self.tool_output.value = ""
        self.prompt_input.value = ""
        self.refined_prompt_output.value = ""
        self.tool_output.value = "All fields cleared."
