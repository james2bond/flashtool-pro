import subprocess
import os
from rich.console import Console

console = Console()

def run_mtkclient(args, timeout=120):
    """Run mtkclient command."""
    cmd = ["mtkclient"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[yellow]{result.stderr}[/yellow]")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]mtkclient command timed out[/red]")
        return False
    except FileNotFoundError:
        console.print("[red]mtkclient not found. Install it first.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]mtkclient error: {e}[/red]")
        return False

def flash_mediatek(firmware_path):
    """
    Flash a MediaTek device using mtkclient.
    Expects firmware_path to be a directory containing partition images.
    """
    if not os.path.isdir(firmware_path):
        console.print(f"[red]Firmware path is not a directory: {firmware_path}[/red]")
        return False

    # Common MediaTek partitions
    partitions = ["boot", "system", "vendor", "recovery", "dtbo", "vbmeta", "logo"]

    images = []
    for part in partitions:
        img_file = os.path.join(firmware_path, f"{part}.img")
        if os.path.exists(img_file):
            images.append((part, img_file))

    if not images:
        console.print("[yellow]No MediaTek image files found in directory.[/yellow]")
        return False

    console.print(f"[cyan]Flashing {len(images)} MediaTek partitions...[/cyan]")
    for part, img in images:
        console.print(f"[bold]Flashing {part}...[/bold]")
        # mtkclient syntax: mtkclient w <partition> <file>
        if not run_mtkclient(["w", part, img]):
            console.print(f"[red]Failed to flash {part}[/red]")
            return False

    # Reboot device
    console.print("[bold]Rebooting device...[/bold]")
    return run_mtkclient(["reset"])
