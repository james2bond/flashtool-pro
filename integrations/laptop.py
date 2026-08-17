import subprocess
from rich.console import Console

console = Console()

def run_fwupd(args, timeout=300):
    """Run fwupdmgr command."""
    cmd = ["fwupdmgr"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[yellow]{result.stderr}[/yellow]")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]fwupdmgr timed out[/red]")
        return False
    except FileNotFoundError:
        console.print("[red]fwupdmgr not found. Install fwupd.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]fwupdmgr error: {e}[/red]")
        return False

def flash_laptop(firmware_file=None, device_id=None):
    """
    Update laptop firmware using fwupd.
    If firmware_file is provided, install that specific CAB file.
    Otherwise, refresh metadata and update all devices.
    """
    if firmware_file:
        console.print(f"[cyan]Installing firmware file: {firmware_file}[/cyan]")
        success = run_fwupd(["install", firmware_file])
        return success
    else:
        console.print("[cyan]Updating all laptop firmware...[/cyan]")
        # Refresh metadata first
        run_fwupd(["refresh"])
        # Get updates (non-interactive)
        success = run_fwupd(["update"])
        return success
