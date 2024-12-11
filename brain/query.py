# /home/daniel/Desktop/Zeal/brain/query.py
import requests
import json

def query_ollama(prompt):
    """Query the Ollama API."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral-large:123b",
                "prompt": prompt,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 80000,
                    "num_ctx": 32768
                }
            },
            timeout=100,
            stream=True
        )
        response.raise_for_status()
        
        result = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    result += data.get("response", "")
                except json.JSONDecodeError as e:
                    # Log error if needed
                    pass
        
        return result.strip() or "No response text received."
    except requests.exceptions.RequestException as e:
        return f"Error querying Ollama: {e}"
