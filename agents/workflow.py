from .ai_client import NVIDIAAIClient
from rich.console import Console

console = Console()

def generate_workflow(device_info: str, firmware_info: str) -> str:
    """Generate a flashing workflow using AI."""
    client = NVIDIAAIClient()
    prompt = f"""
You are a flashing workflow automation expert.

Device:
{device_info}

Firmware:
{firmware_info}

Create a detailed, step-by-step flashing workflow for this specific device and firmware. Include:

1. Pre-flash checks (battery level, backup, etc.)
2. How to boot into the correct mode (download, fastboot, EDL, etc.)
3. Exact flashing commands or tool usage.
4. Verification steps after flashing.
5. What to do if something fails.

Use only official firmware and authorized tools. Do not include any steps to bypass security locks.
"""
    console.print("[cyan]AI is generating workflow...[/cyan]")
    response = client.generate(prompt)
    return response
