import os
import requests
from rich.console import Console

console = Console()

class NVIDIAAIClient:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            console.print("[red]NVIDIA_API_KEY not set. Please export it or add to .env[/red]")
            raise ValueError("Missing NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.model = "meta/llama-3.1-70b-instruct"

    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.2) -> str:
        """Send a prompt to NVIDIA API and return the response text."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                console.print(f"[red]NVIDIA API error {response.status_code}: {response.text}[/red]")
                return f"Error: API returned {response.status_code}"
        except Exception as e:
            console.print(f"[red]NVIDIA API request failed: {e}[/red]")
            return f"Error: {str(e)}"
