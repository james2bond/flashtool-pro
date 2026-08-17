import os
import time
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

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.2, retries: int = 2) -> str:
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
        for attempt in range(retries):
            try:
                console.print(f"[dim]Attempt {attempt+1}/{retries}...[/dim]")
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=120
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"].strip()
                else:
                    console.print(f"[yellow]NVIDIA API error {response.status_code}: {response.text[:200]}[/yellow]")
                    if response.status_code == 401:
                        console.print("[red]Invalid API key. Check NVIDIA_API_KEY.[/red]")
                        return "Error: Invalid API key"
                    if response.status_code == 404:
                        console.print("[red]Model not found. Check model name.[/red]")
                        return "Error: Model not found"
                    # Wait before retry
                    time.sleep(2)
            except requests.exceptions.Timeout:
                console.print(f"[yellow]Timeout on attempt {attempt+1}. Retrying...[/yellow]")
                time.sleep(2)
            except Exception as e:
                console.print(f"[red]Request failed: {e}[/red]")
                time.sleep(2)
        return "Error: API request failed after retries"
