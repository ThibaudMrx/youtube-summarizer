# ollama.py

import requests
from typing import Optional
import json
from CONFIG import *


class OllamaClient:
    def __init__(self, model: str = OLLAMA_MODEL, ollama_url: str = OLLAMA_CLIENT_URL):
        """
        Initializes the OllamaClient with the specified model and server URL.

        :param model: The default model to use for completions.
        :param ollama_url: The base URL of the Ollama server.
        """
        self.model = model
        self.ollama_url = ollama_url
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"OllamaClient initialized with model='{self.model}' and URL='{self.ollama_url}'")

    def get_completion(self, prompt: str, model: Optional[str] = None) -> str:
        """
        Sends a prompt to the Ollama server and retrieves the completion.

        :param prompt: The prompt text to send.
        :param model: (Optional) The model to use for this request. Defaults to the initialized model.
        :return: The completion text from Ollama.
        """
        chosen_model = model if model else self.model
        payload = {
            "model": chosen_model,
            "prompt": prompt,
            "stream": False,
        }
        endpoint = f"{self.ollama_url}/api/generate"
        self.logger.debug(f"Sending POST request to {endpoint} with payload: {str(payload)[:50]}")

        try:
            resp = requests.post(endpoint, json=payload)
            resp.raise_for_status()
            resp_decode = resp.content.decode('utf-8')
            resp_json = json.loads(resp_decode)
            answer = resp_json['response']
            return answer
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error communicating with Ollama: {e}")
            raise

    def close(self):
        """Closes the underlying HTTP session."""
        self.session.close()
        self.logger.debug("HTTP session closed.")
