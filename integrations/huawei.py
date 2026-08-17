import subprocess
import os
from rich.console import Console
from integrations.fastboot import flash_fastboot

console = Console()

def flash_huawei(serial, firmware_path):
    """
    Flash a Huawei device using fastboot.
    Note: Some Huawei devices may require specific tools; fastboot works for many models.
    """
    console.print("[cyan]Huawei device detected. Using fastboot method...[/cyan]")
    return flash_fastboot(serial, firmware_path)
