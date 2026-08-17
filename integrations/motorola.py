import subprocess
import os
from rich.console import Console
from integrations.fastboot import flash_fastboot

console = Console()

def flash_motorola(serial, firmware_path):
    """
    Flash a Motorola device using fastboot.
    """
    console.print("[cyan]Motorola device detected. Using fastboot method...[/cyan]")
    return flash_fastboot(serial, firmware_path)
