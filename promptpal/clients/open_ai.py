# promptpal/clients/open_ai.py

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

from promptpal.clients.client import Client


@dataclass
class OpenAIResponse:
    """Wrapper for OpenAI response"""

    content: str
    usage: any


class OpenAIClient(Client):
    """
    Client for interacting with OpenAI API
    """

    def __init__(self, openai_api_key: str = None):
        if not openai_api_key:
            # check if the api key has been set to OPEN_API_KEY
            openai_api_key = os.getenv("OPENAI_API_KEY")

            if not openai_api_key:
                raise ValueError(
                    "API key is required to use the OpenAI client. "
                    "Set the OPENAI_API_KEY environment variable or pass it into the client as a parameter."
                )

        self.client = OpenAI(api_key=openai_api_key)
        self.thread = None

    @property
    def thread(self):
        """Get current thread or create new one"""
        if not self._thread:
            self._thread = self.client.beta.threads.create()
        return self._thread

    @thread.setter
    def thread(self, value):
        self._thread = value

    def process_request(
        self,
        prompt: str,
        role: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        top_p: float = 1.0,
    ) -> OpenAIResponse:
        """
        Process a request through the OpenAI API

        Args:
            prompt: The input prompt
            role: System role instructions
            model: Model to use
            temperature: Temperature setting
            top_p: Top p setting

        Returns:
            Wrapped response object
        """
        # Create message in thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id, role="user", content=prompt
        )

        # Create and run assistant
        assistant = self.client.beta.assistants.create(
            name="Agent", instructions=role, model=model
        )

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id, assistant_id=assistant.id
        )

        # Wait for completion
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id, run_id=run.id
            )
            if run_status.status in ["completed", "failed"]:
                break

        # Get response
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)

        if not messages.data:
            raise RuntimeError("No response received from OpenAI")

        return OpenAIResponse(
            content=messages.data[0].content[0].text.value, usage=run_status.usage
        )
