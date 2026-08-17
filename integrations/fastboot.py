import subprocess
from rich.console import Console

console = Console()

def run_fastboot(serial, args):
    """Run a fastboot command for a specific device."""
    cmd = ["fastboot", "-s", serial] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, check=True)
        console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[yellow]{result.stderr}[/yellow]")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]Fastboot command timed out[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Fastboot error: {e}[/red]")
        return False

def flash_fastboot(serial, firmware_path):
    """Flash a fastboot-flashable firmware package (assumes extracted images)."""
    # Expected firmware_path is a directory containing *.img files
    import os
    if not os.path.isdir(firmware_path):
        console.print(f"[red]Firmware path is not a directory: {firmware_path}[/red]")
        return False

    images = []
    # Common partitions to flash
    partition_names = ["boot", "system", "vendor", "recovery", "dtbo", "vbmeta"]
    for part in partition_names:
        img_file = os.path.join(firmware_path, f"{part}.img")
        if os.path.exists(img_file):
            images.append((part, img_file))

    if not images:
        console.print("[yellow]No image files found in firmware directory.[/yellow]")
        return False

    console.print(f"[cyan]Flashing {len(images)} partitions...[/cyan]")
    for part, img in images:
        console.print(f"[bold]Flashing {part}...[/bold]")
        if not run_fastboot(serial, ["flash", part, img]):
            console.print(f"[red]Failed to flash {part}[/red]")
            return False

    # Reboot
    console.print("[bold]Rebooting device...[/bold]")
    return run_fastboot(serial, ["reboot"])
