from IPython.display import display
import ipywidgets as widgets
from typing import List, Optional


class PromptpalUI:
    def __init__(self):
        # Prompt Pal Widget UI for Notebooks
        self._selected_agent_names: List[str] = []

        # Configure Team Tab
        self.agent_dropdown = widgets.Dropdown(
            options=[
                "artist",
                "assistant",
                "data_scientist",
                "data_visualization",
                "developer",
                "editor",
                "image",
                "photographer",
                "prompt_engineer",
                "refactor",
                "unit_test",
                "writer",
            ],
            value="assistant",
            description="Agent Role:",
        )

        # Add agents to team dropdown and "Add" buttons
        self.add_agent_button = widgets.Button(description="Add Agent")
        self.add_agent_button.on_click(self._add_agent_cb)

        # Display showing selected agents with a button to remove the agent
        self.selected_agents = widgets.VBox([])

        # Reset button
        self.reset_button = widgets.Button(description="Reset")
        self.reset_button.on_click(self._reset_cb)

        self.add_agents_tab = widgets.Box(
            [
                widgets.HTML("<h2>Select Agent Roles</h2>"),
                widgets.HBox([self.agent_dropdown, self.add_agent_button]),
                self.selected_agents,
                self.reset_button,
            ]
        )

        # Configuration Tab
        self.model_selection = widgets.Dropdown(
            options=["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"], description="Model:"
        )

        self.write_code_to_files_check = widgets.Checkbox(
            description="Write code to files", value=False
        )

        self.log_level = widgets.Dropdown(
            options=["ERROR", "INFO", "DEBUG"], description="Log Level:", value="INFO"
        )

        self.configuration_tab = widgets.Box(
            [
                widgets.HTML("<h2>Configuration</h2>"),
                self.model_selection,
                self.write_code_to_files_check,
                self.log_level,
            ]
        )

        # Custom Agent Tab
        self.custom_agent_name = widgets.Text(
            description="Name:", placeholder="Enter agent name"
        )

        self.custom_agent_prompt = widgets.Textarea(
            description="Prompt:", placeholder="Enter agent prompt/instructions"
        )

        self.refine_prompt_toggle = widgets.ToggleButtons(
            options=["Yes", "No"], description="Refine Prompt:", value="No"
        )

        self.glyph_refinement_check = widgets.Checkbox(
            description="Use Glyph Refinement", value=False
        )

        self.chain_of_though_refinement_check = widgets.Checkbox(
            description="Use Chain of Thought", value=False
        )

        self.add_custom_agent_button = widgets.Button(description="Add Custom Agent")
        self.add_custom_agent_button.on_click(self._add_custom_agent_cb)

        self.custom_agent_tab = widgets.Box(
            [
                widgets.HTML("<h2>Custom Agent</h2>"),
                self.custom_agent_name,
                self.custom_agent_prompt,
                self.refine_prompt_toggle,
                self.glyph_refinement_check,
                self.chain_of_though_refinement_check,
                self.add_custom_agent_button,
            ]
        )

        # Instructions Tab
        self.instructions = widgets.HTML("""
            <p>Configure and create a team of AI agents to assist in your work. Once created, press <strong>"Create Team"</strong> and then chat with the team object.</p>
            <pre>
            pal = PromptPalUI()
            pal.display()
            ...configure your agent team and press "Create Team"
            team = pal.get_team()
            team.chat('Write a program that calculates pi')
            </pre>

            <p>The team will have a shared <strong>"thread"</strong> of context. You can press <strong>"New Thread"</strong>, which will create a fresh thread for the team to operate on.</p>
        """)

        self.instructions_tab = widgets.Box(
            [widgets.HTML("<h2>Instructions</h2>"), self.instructions]
        )

        # Status Tab
        self.token_display = widgets.HTML("Total Tokens: 0")
        self.cost_display = widgets.HTML("Total Cost: $0.00")
        self.log_display = widgets.Textarea(
            description="Logs:",
            disabled=True,
            layout=widgets.Layout(width="100%", height="200px"),
        )
        self.status_message = widgets.HTML("Status: No team created")

        self.status_tab = widgets.Box(
            [
                widgets.HTML("<h2>Status</h2>"),
                self.token_display,
                self.cost_display,
                self.log_display,
                self.status_message,
            ]
        )

        # Main Interface
        self.tabs = widgets.Tab()
        self.tabs.children = [
            self.add_agents_tab,
            self.configuration_tab,
            self.custom_agent_tab,
            self.instructions_tab,
            self.status_tab,
        ]
        self.tabs.set_title(0, "Add Agents")
        self.tabs.set_title(1, "Configuration")
        self.tabs.set_title(2, "Custom Agent")
        self.tabs.set_title(3, "Instructions")
        self.tabs.set_title(4, "Status")

        self.interface = widgets.Box([widgets.HTML("<h1>PromptPal</h1>"), self.tabs])

    def display(self):
        """Display the UI interface"""
        display(self.interface)

    def _add_agent_cb(self, b):
        """Callback for adding a predefined agent"""
        agent_name = self.agent_dropdown.value
        if agent_name not in self._selected_agent_names:
            self._selected_agent_names.append(agent_name)
            agent_widget = SelectedAgentWidget(agent_name, self._remove_agent)
            self.selected_agents.children = list(self.selected_agents.children) + [
                agent_widget.interface
            ]

            # Remove from dropdown options
            new_options = [
                opt for opt in self.agent_dropdown.options if opt != agent_name
            ]
            self.agent_dropdown.options = new_options
            if new_options:
                self.agent_dropdown.value = new_options[0]

    def _add_custom_agent_cb(self, b):
        """Callback for adding a custom agent"""
        name = self.custom_agent_name.value
        if name and name not in self._selected_agent_names:
            self._selected_agent_names.append(name)
            agent_widget = SelectedAgentWidget(name, self._remove_agent)
            self.selected_agents.children = list(self.selected_agents.children) + [
                agent_widget.interface
            ]

            # Clear inputs
            self.custom_agent_name.value = ""
            self.custom_agent_prompt.value = ""
            self.refine_prompt_toggle.value = "No"
            self.glyph_refinement_check.value = False
            self.chain_of_though_refinement_check.value = False

    def _remove_agent(self, agent_name: str):
        """Remove an agent from the selected agents"""
        if agent_name in self._selected_agent_names:
            self._selected_agent_names.remove(agent_name)

            # Update selected agents display
            new_children = [
                child
                for child in self.selected_agents.children
                if agent_name not in str(child.children[0].value)
            ]
            self.selected_agents.children = new_children

            # Add back to dropdown if it was a predefined agent
            if agent_name in [
                "artist",
                "assistant",
                "data_scientist",
                "data_visualization",
                "developer",
                "editor",
                "image",
                "photographer",
                "prompt_engineer",
                "refactor",
                "unit_test",
                "writer",
            ]:
                self.agent_dropdown.options = sorted(
                    list(self.agent_dropdown.options) + [agent_name]
                )

    def _reset_cb(self, b):
        """Reset the UI to initial state"""
        self._selected_agent_names = []
        self.selected_agents.children = []
        self.agent_dropdown.options = [
            "artist",
            "assistant",
            "data_scientist",
            "data_visualization",
            "developer",
            "editor",
            "image",
            "photographer",
            "prompt_engineer",
            "refactor",
            "unit_test",
            "writer",
        ]
        self.agent_dropdown.value = "assistant"
        self.model_selection.value = "gpt-4o-mini"
        self.write_code_to_files_check.value = False
        self.log_level.value = "INFO"
        self.custom_agent_name.value = ""
        self.custom_agent_prompt.value = ""
        self.refine_prompt_toggle.value = "No"
        self.glyph_refinement_check.value = False
        self.chain_of_though_refinement_check.value = False
        self.token_display.value = "Total Tokens: 0"
        self.cost_display.value = "Total Cost: $0.00"
        self.log_display.value = ""
        self.status_message.value = "Status: No team created"


class SelectedAgentWidget:
    def __init__(self, agent_name: str, remove_agent_cb):
        self.agent_name = agent_name
        self.agent_label = widgets.Label(agent_name)
        self.remove_agent_button = widgets.Button(description="X")
        self.remove_agent_button.on_click(self.remove_cb)
        self.remove_agent_cb = remove_agent_cb

        self.interface = widgets.HBox([self.agent_label, self.remove_agent_button])

    def remove_cb(self, b):
        self.remove_agent_cb(self.agent_name)
