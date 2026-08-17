import subprocess
import os
from rich.console import Console

console = Console()

def run_idevicerestore(args, timeout=600):
    """Run idevicerestore command."""
    cmd = ["idevicerestore"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[yellow]{result.stderr}[/yellow]")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]idevicerestore timed out[/red]")
        return False
    except FileNotFoundError:
        console.print("[red]idevicerestore not found. Install libimobiledevice-utils.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]idevicerestore error: {e}[/red]")
        return False

def flash_apple(ipsw_path):
    """
    Restore an Apple device using official IPSW.
    ipsw_path: path to .ipsw firmware file.
    """
    if not os.path.isfile(ipsw_path):
        console.print(f"[red]IPSW file not found: {ipsw_path}[/red]")
        return False

    console.print("[cyan]Restoring Apple device with IPSW...[/cyan]")
    console.print("[yellow]Make sure device is in DFU or Recovery mode.[/yellow]")
    # idevicerestore <ipsw> -e (erase) or -u (update)
    success = run_idevicerestore([ipsw_path])

    if success:
        console.print("[bold]Apple restore completed successfully.[/bold]")
    else:
        console.print("[red]Apple restore failed.[/red]")
    return success
