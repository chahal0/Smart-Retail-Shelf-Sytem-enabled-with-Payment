import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3"

def query_ollama(prompt, model=DEFAULT_MODEL):
    """
    Sends a prompt to the local Ollama instance and returns the generated text.
    """
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120 # longer timeout for local model
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {str(e)}. Make sure Ollama is running."
