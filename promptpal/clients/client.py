# promptpal/clients/client

from abc import ABC, abstractmethod
from typing import Any


class Client(ABC):
    """Abstract base class for API clients"""

    @property
    @abstractmethod
    def thread(self):
        """Abstract property for getting/creating thread"""
        pass

    @thread.setter
    @abstractmethod
    def thread(self, value):
        """Abstract setter for thread property"""
        pass

    @abstractmethod
    def process_request(
        self,
        prompt: str,
        role: str,
        model: str,
        temperature: float = 0.7,
        top_p: float = 1.0,
    ) -> Any:
        """
        Abstract method to process a request through the API

        Args:
            prompt: The input prompt
            role: System role instructions
            model: Model to use
            temperature: Temperature setting
            top_p: Top p setting

        Returns:
            Response object
        """
        pass
