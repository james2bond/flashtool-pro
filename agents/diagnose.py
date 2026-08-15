from .ai_client import NVIDIAAIClient
from rich.console import Console

console = Console()

def diagnose_device(device_info: str, logs: str = "") -> str:
    """Run AI diagnostics on a device."""
    client = NVIDIAAIClient()
    prompt = f"""
You are a senior firmware repair engineer with 20 years experience.

Device information:
{device_info}

Logs (if any):
{logs}

Provide:
1. Diagnosis of the device state.
2. Recommended official firmware version.
3. Step-by-step flashing procedure using official tools.
4. Potential issues and how to avoid them.
5. Verification steps after flashing.

Important: Only recommend official firmware and authorized repair methods. Do not suggest bypassing FRP, iCloud, carrier locks, or any security protections.
"""
    console.print("[cyan]AI is analyzing device...[/cyan]")
    response = client.generate(prompt)
    return response
