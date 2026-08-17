import subprocess
import os
from rich.console import Console

console = Console()

def run_qdl(args, timeout=180):
    """Run qdl command."""
    cmd = ["qdl"] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[yellow]{result.stderr}[/yellow]")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]qdl command timed out[/red]")
        return False
    except FileNotFoundError:
        console.print("[red]qdl not found. Install it first.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]qdl error: {e}[/red]")
        return False

def flash_qualcomm_edl(firmware_path, programmer_path=None):
    """
    Flash a Qualcomm device in EDL mode using qdl.
    firmware_path: directory containing rawprogram XML and images.
    programmer_path: optional Firehose programmer file.
    """
    if not os.path.isdir(firmware_path):
        console.print(f"[red]Firmware path is not a directory: {firmware_path}[/red]")
        return False

    # Typical qdl usage:
    # qdl [--storage ufs|emmc] [prog_firehose.mbn] rawprogram0.xml patch0.xml
    args = []

    # If programmer provided, include it
    if programmer_path and os.path.exists(programmer_path):
        args.append(programmer_path)

    # Add XML files if they exist
    for xml in ["rawprogram0.xml", "patch0.xml"]:
        xml_path = os.path.join(firmware_path, xml)
        if os.path.exists(xml_path):
            args.append(xml_path)
        else:
            console.print(f"[yellow]Warning: {xml} not found in {firmware_path}[/yellow]")

    if not args:
        console.print("[yellow]No programmer or XML files found for Qualcomm flashing.[/yellow]")
        return False

    console.print("[cyan]Flashing Qualcomm EDL device...[/cyan]")
    success = run_qdl(args)

    if success:
        console.print("[bold]Qualcomm flashing completed. Device should reboot.[/bold]")
    return success
