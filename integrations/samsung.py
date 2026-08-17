import subprocess
import os
from rich.console import Console

console = Console()

def run_heimdall(serial, args):
    """Run a heimdall command for a specific device."""
    # Heimdall usually auto-detects, but we can pass --usb if needed
    cmd = ["heimdall"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[yellow]{result.stderr}[/yellow]")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]Heimdall command timed out[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Heimdall error: {e}[/red]")
        return False

def flash_samsung(firmware_path):
    """Flash a Samsung firmware package using Heimdall."""
    if not os.path.isdir(firmware_path):
        console.print(f"[red]Firmware path is not a directory: {firmware_path}[/red]")
        return False

    # Samsung firmware typically has these files: boot.img, system.img, recovery.img, etc.
    # Heimdall uses --<PARTITION> flags.
    partition_map = {
        "BOOT": "boot.img",
        "RECOVERY": "recovery.img",
        "SYSTEM": "system.img",
        "VENDOR": "vendor.img",
        "RADIO": "modem.bin",
    }

    args = []
    for part, filename in partition_map.items():
        file_path = os.path.join(firmware_path, filename)
        if os.path.exists(file_path):
            args.extend([f"--{part}", file_path])

    if not args:
        console.print("[yellow]No compatible Samsung firmware files found.[/yellow]")
        return False

    console.print("[cyan]Flashing Samsung firmware with Heimdall...[/cyan]")
    success = run_heimdall(None, ["flash"] + args)
    if success:
        console.print("[bold]Rebooting device...[/bold]")
        run_heimdall(None, ["reboot"])
    return success
