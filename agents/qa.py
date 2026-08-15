from .ai_client import NVIDIAAIClient
from rich.console import Console

console = Console()

def qa_job(job_logs: str) -> str:
    """Review flashing logs and determine success/failure."""
    client = NVIDIAAIClient()
    prompt = f"""
You are a quality assurance expert for firmware flashing.

Review these flashing logs:

{job_logs}

Determine if the job succeeded, failed, or needs review. Check for:
- Firmware checksum match
- Flash success messages
- Boot verification
- Any errors or warnings

Respond with exactly one of: SUCCESS, FAILED, NEEDS_REVIEW
Then provide a brief explanation.
"""
    console.print("[cyan]AI is reviewing logs...[/cyan]")
    response = client.generate(prompt, max_tokens=500)
    return response
