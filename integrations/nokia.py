import subprocess
import os
from rich.console import Console
from integrations.fastboot import flash_fastboot

console = Console()

def flash_nokia(serial, firmware_path):
    """
    Flash a Nokia device using fastboot.
    Nokia stock ROMs are usually fastboot-flashable.
    """
    console.print("[cyan]Nokia device detected. Using fastboot method...[/cyan]")
    return flash_fastboot(serial, firmware_path)
