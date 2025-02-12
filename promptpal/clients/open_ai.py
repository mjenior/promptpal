# promptpal/clients/open_ai.py

import os

from openai import OpenAI

from promptpal.clients.client import Client


class OpenAIClient(Client):
    """
    Client for interacting with OpenAPI
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

    @property
    def thread(self):
        if not self.thread:
            self.thread = self.client.beta.threads.create()
        else:
            return self.thread
