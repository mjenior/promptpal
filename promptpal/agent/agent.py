# promptpal/agent/agent.py

import os
from datetime import datetime
from typing import Optional, Dict, Any

from promptpal.agent.agent_config import AgentConfig
from promptpal.agent.agent_role import AgentRole
from promptpal.clients.client import Client


class Agent:
    """
    Represents an individual agent with specific configuration and capabilities
    """

    def __init__(self, config: AgentConfig, role: AgentRole, client: Client):
        self.config = config
        self.role = role
        self.client = client

        # Initialize tracking variables
        self.tokens = {"prompt": 0, "completion": 0}
        self.cost = {"prompt": 0.0, "completion": 0.0}
        self.last_message: Optional[str] = None

        # Set up logging if enabled
        if self.config.logging:
            self._setup_logging()

    def request(self, prompt: str = "") -> str:
        """
        Process a request using the configured client

        Args:
            prompt: The input prompt to process

        Returns:
            The processed response
        """
        # Use last message if no prompt provided
        if not prompt and self.last_message:
            prompt = self.last_message
        elif not prompt:
            raise ValueError("No prompt provided and no existing messages found")

        # Prepare the prompt
        prepared_prompt = self._prepare_prompt(prompt)

        # Process request through client
        response = self.client.process_request(
            prompt=prepared_prompt,
            role=self.role.prompt,
            model=self.config.model,
            temperature=self.config.temperature,
            top_p=self.config.top_p,
        )

        # Update tracking
        self._update_usage(response)
        self.last_message = response.content

        # Log if enabled
        if self.config.logging:
            self._log_interaction(prompt, response.content)

        return response.content

    def _prepare_prompt(self, prompt: str) -> str:
        """Prepare the prompt with any configured modifications"""
        if self.config.use_chain_of_thought:
            # Add chain of thought instructions
            prompt += "\n\nUse chain of thought reasoning to solve this problem."

        if self.config.use_glyph_promts:
            # Add glyph formatting instructions
            prompt += "\n\nFormat response using glyph structure."

        return prompt

    def _setup_logging(self):
        """Initialize logging setup"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = f"logs/agent_{timestamp}.log"
        os.makedirs("logs", exist_ok=True)

        with open(self.log_file, "w") as f:
            f.write(f"Agent initialized with role: {self.role.name}\n")

    def _log_interaction(self, prompt: str, response: str):
        """Log an interaction to the log file"""
        with open(self.log_file, "a") as f:
            f.write(f"\nPrompt: {prompt}\n")
            f.write(f"Response: {response}\n")
            f.write("-" * 80 + "\n")

    def _update_usage(self, response: Any):
        """Update token and cost tracking"""
        # Update tokens
        self.tokens["prompt"] += response.usage.prompt_tokens
        self.tokens["completion"] += response.usage.completion_tokens

        # Calculate costs (simplified example rates)
        self.cost["prompt"] += response.usage.prompt_tokens * 0.0001
        self.cost["completion"] += response.usage.completion_tokens * 0.0002
