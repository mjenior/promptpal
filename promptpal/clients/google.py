# promptpal/clients/open_ai.py

import os

from google import genai

from promptpal.clients.client import Client


class GoogleClient(Client):
    """
    Client for interacting with Google
    """

    def __init__(self, google_api_key: str = None):
        if not google_api_key:
            # check if the api key has been set to OPEN_API_KEY
            google_api_key = os.getenv("GEMINI_API_KEY")

            if not google_api_key:
                raise ValueError(
                    "API key is required to use the Google client. "
                    "Set the GEMINI_API_KEY environment variable or pass it into the client as a parameter."
                )

        self.client = genai.Client(api_key=google_api_key)

    @property
    def thread(self):
        if not self.chat:
            self.chat = self.client.chats.create(model="gemini-2.0-flash")
        else:
            return self.chat
