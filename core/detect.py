import subprocess
from rich.console import Console
from rich.table import Table

console = Console()

def run_command(cmd, timeout=10):
    """Run a shell command and return stdout, stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "Command timed out"
    except FileNotFoundError:
        return "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return "", str(e)

def detect_adb_devices():
    """Return list of ADB devices."""
    stdout, stderr = run_command(["adb", "devices", "-l"])
    devices = []
    if stdout:
        lines = stdout.strip().split("\n")[1:]  # skip header
        for line in lines:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    serial = parts[0]
                    state = parts[1]
                    model = ""
                    # extract model from -l output
                    for part in parts[2:]:
                        if part.startswith("model:"):
                            model = part.split(":",1)[1]
                            break
                    devices.append({
                        "serial": serial,
                        "state": state,
                        "model": model,
                        "mode": "ADB"
                    })
    return devices

def detect_fastboot_devices():
    """Return list of fastboot devices."""
    stdout, stderr = run_command(["fastboot", "devices"])
    devices = []
    if stdout:
        for line in stdout.strip().split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({
                        "serial": parts[0],
                        "state": parts[1],
                        "model": "",
                        "mode": "FASTBOOT"
                    })
    return devices

def detect_usb_devices():
    """Return list of USB devices (raw lsusb output)."""
    stdout, stderr = run_command(["lsusb"])
    devices = []
    if stdout:
        for line in stdout.strip().split("\n"):
            if line.strip():
                devices.append(line.strip())
    return devices

def detect_all():
    """Detect all devices and print summary."""
    console.print("[bold cyan]Scanning for devices...[/bold cyan]\n")

    adb_devices = detect_adb_devices()
    fastboot_devices = detect_fastboot_devices()
    usb_devices = detect_usb_devices()

    # Print ADB devices
    if adb_devices:
        table = Table(title="ADB Devices", show_header=True, header_style="bold green")
        table.add_column("Serial")
        table.add_column("State")
        table.add_column("Model")
        for d in adb_devices:
            table.add_row(d["serial"], d["state"], d["model"])
        console.print(table)
    else:
        console.print("[yellow]No ADB devices found.[/yellow]")

    # Print Fastboot devices
    if fastboot_devices:
        table = Table(title="Fastboot Devices", show_header=True, header_style="bold green")
        table.add_column("Serial")
        table.add_column("State")
        for d in fastboot_devices:
            table.add_row(d["serial"], d["state"])
        console.print(table)
    else:
        console.print("[yellow]No Fastboot devices found.[/yellow]")

    # Print USB devices (first 20, just to show something)
    if usb_devices:
        console.print("\n[bold]USB Devices (raw):[/bold]")
        for dev in usb_devices[:20]:
            console.print(f"  {dev}")
        if len(usb_devices) > 20:
            console.print(f"  ... and {len(usb_devices)-20} more")
    else:
        console.print("[yellow]No USB devices found.[/yellow]")

    # Return a combined list for programmatic use
    all_devices = adb_devices + fastboot_devices
    return all_devices
