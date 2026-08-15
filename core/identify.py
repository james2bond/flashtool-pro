import subprocess
from rich.console import Console
from rich.table import Table

console = Console()

# USB VID:PID to chipset/mode mapping
USB_VID_PID_MAP = {
    "05c6:9008": "Qualcomm EDL (Emergency Download) mode",
    "05c6:900e": "Qualcomm QDLoader 9008 mode",
    "0e8d:2000": "MediaTek PreLoader mode",
    "0e8d:2001": "MediaTek DA mode",
    "04e8:685d": "Samsung Download mode (Odin)",
    "18d1:4ee0": "Google Fastboot mode",
    "18d1:d00d": "Google ADB mode",
    "2a70:f003": "Xiaomi Fastboot mode",
    "2717:ff08": "Xiaomi ADB mode",
    "05c6:9091": "Qualcomm Diagnostic mode",
    "1d6b:0002": "USB 2.0 Hub",
    "1d6b:0003": "USB 3.0 Hub",
}

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

def get_adb_properties(serial):
    """Get relevant device properties via ADB."""
    stdout, stderr = run_command(["adb", "-s", serial, "shell", "getprop"])
    props = {}
    if stdout:
        for line in stdout.splitlines():
            if ":" in line:
                # Format: [key]: [value]
                key_val = line.split(":", 1)
                if len(key_val) == 2:
                    key = key_val[0].strip().strip('[]')
                    value = key_val[1].strip().strip('[]')
                    props[key] = value
    return props

def identify_adb(serial):
    """Identify device via ADB properties."""
    props = get_adb_properties(serial)
    info = {
        "serial": serial,
        "mode": "ADB",
        "model": props.get("ro.product.model", ""),
        "manufacturer": props.get("ro.product.manufacturer", ""),
        "chipset": props.get("ro.board.platform") or props.get("ro.hardware", ""),
        "android_version": props.get("ro.build.version.release", ""),
        "firmware": props.get("ro.build.display.id", ""),
    }
    return info

def identify_fastboot(serial):
    """Identify device via fastboot getvar."""
    info = {
        "serial": serial,
        "mode": "FASTBOOT",
        "model": "",
        "manufacturer": "",
        "chipset": "",
        "android_version": "",
        "firmware": "",
    }
    # Try common fastboot variables
    for var in ["product", "model", "board", "hw-revision"]:
        stdout, stderr = run_command(["fastboot", "-s", serial, "getvar", var])
        if stdout and "unknown" not in stdout.lower():
            if var == "product":
                info["model"] = stdout.strip()
            elif var == "model":
                if not info["model"]:
                    info["model"] = stdout.strip()
            elif var == "board":
                info["chipset"] = stdout.strip()
    return info

def identify_usb():
    """Identify devices from lsusb output using VID:PID mapping."""
    stdout, stderr = run_command(["lsusb"])
    devices = []
    if stdout:
        for line in stdout.splitlines():
            parts = line.split()
            if len(parts) >= 6:
                # Format: Bus 001 Device 002: ID 05c6:9008 Qualcomm, Inc. ...
                # The ID is at position 5 (0-indexed)
                id_part = parts[5] if len(parts) > 5 else ""
                if ":" in id_part:
                    vid_pid = id_part.split(":")[0] + ":" + id_part.split(":")[1]
                    if vid_pid in USB_VID_PID_MAP:
                        devices.append({
                            "serial": f"USB-{id_part}",
                            "mode": "USB",
                            "model": USB_VID_PID_MAP[vid_pid],
                            "chipset": vid_pid,
                            "manufacturer": "",
                        })
    return devices

def identify_all():
    """Identify all connected devices and print summary."""
    console.print("[bold cyan]Identifying devices...[/bold cyan]\n")

    # ADB devices
    stdout, _ = run_command(["adb", "devices"])
    adb_serials = []
    if stdout:
        for line in stdout.strip().split("\n")[1:]:
            if line.strip() and "device" in line:
                serial = line.split()[0]
                adb_serials.append(serial)

    # Fastboot devices
    stdout, _ = run_command(["fastboot", "devices"])
    fb_serials = []
    if stdout:
        for line in stdout.strip().split("\n"):
            if line.strip():
                serial = line.split()[0]
                fb_serials.append(serial)

    identified_devices = []

    # Identify ADB devices
    for serial in adb_serials:
        info = identify_adb(serial)
        identified_devices.append(info)

    # Identify fastboot devices
    for serial in fb_serials:
        info = identify_fastboot(serial)
        identified_devices.append(info)

    # Identify USB-only devices (not in ADB/fastboot)
    usb_devices = identify_usb()
    # Filter out devices already identified by ADB/fastboot serials
    existing_serials = set(adb_serials + fb_serials)
    for usb_dev in usb_devices:
        # Simple check: if USB device contains VID:PID pattern that's not already seen
        identified_devices.append(usb_dev)

    # Print results in a table
    if identified_devices:
        table = Table(title="Identified Devices", show_header=True, header_style="bold green")
        table.add_column("Serial")
        table.add_column("Mode")
        table.add_column("Model")
        table.add_column("Manufacturer")
        table.add_column("Chipset")
        table.add_column("Android")

        for dev in identified_devices:
            table.add_row(
                dev.get("serial", ""),
                dev.get("mode", ""),
                dev.get("model", ""),
                dev.get("manufacturer", ""),
                dev.get("chipset", ""),
                dev.get("android_version", "")
            )
        console.print(table)
    else:
        console.print("[yellow]No devices identified.[/yellow]")

    return identified_devices
