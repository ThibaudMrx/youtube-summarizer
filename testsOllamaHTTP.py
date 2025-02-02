#!/usr/bin/env python3

"""
test_ollama.py

Usage:
    python test_ollama.py
"""

import requests
import sys
import json
from CONFIG import *

DEFAULT_MODEL = "mistral"  # Change to the model you prefer, e.g. "llama2", "my-custom-model", etc.

def ollama_complete(prompt, model, ollama_url):
    """
    Send a prompt to Ollama via HTTP POST and return the completion text.
    """
    url = f"{ollama_url}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    print(f"Sending request to {url} with payload:\n{payload}\n")

    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        resp_content = resp.content
        resp_decode = resp_content.decode('utf-8')
        resp_json = json.loads(resp_decode)
        answer = resp_json['response']
        return answer
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def run_tests(ollama_url=OLLAMA_CLIENT_URL, model=DEFAULT_MODEL):
    print(f"\n--- Testing Ollama at {ollama_url} with model '{model}' ---\n")

    # Test 1: Simple greeting prompt
    prompt_1 = "Hello! How are you?"
    print(f"Prompt: {prompt_1}")
    response_1 = ollama_complete(prompt_1, model, ollama_url)
    print(f"Ollama Response:\n{response_1}\n")

    # Test 2: Something more specific
    prompt_2 = "Explain the concept of gravity in one short paragraph."
    print(f"Prompt: {prompt_2}")
    response_2 = ollama_complete(prompt_2, model, ollama_url)
    print(f"Ollama Response:\n{response_2}\n")

    # Test 3: Another example (you can add more as needed)
    prompt_3 = "List three uses for a paperclip."
    print(f"Prompt: {prompt_3}")
    response_3 = ollama_complete(prompt_3, model, ollama_url)
    print(f"Ollama Response:\n{response_3}\n")

    print("--- Tests completed ---\n")


if __name__ == "__main__":
    # Optionally grab URL/model from sys.argv or environment
    # For brevity, we just call run_tests with defaults:
    run_tests()
