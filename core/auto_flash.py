import time
import subprocess
from rich.console import Console
from rich.table import Table

from db.database import get_session, init_db
from db.models import Device, Firmware, Job
from core.identify import identify_adb, identify_fastboot, identify_usb
from core.flash import flash_device
from core.queue import _process_job

console = Console()

def get_connected_serials():
    """Return a set of connected device serials (ADB and fastboot)."""
    serials = set()
    # ADB
    try:
        adb_out = subprocess.check_output(["adb", "devices"], text=True, timeout=5)
        for line in adb_out.strip().split("\n")[1:]:
            if line.strip() and "device" in line:
                serial = line.split()[0]
                serials.add(serial)
    except Exception:
        pass
    # Fastboot
    try:
        fb_out = subprocess.check_output(["fastboot", "devices"], text=True, timeout=5)
        for line in fb_out.strip().split("\n"):
            if line.strip():
                serial = line.split()[0]
                serials.add(serial)
    except Exception:
        pass
    return serials

def store_device(serial: str):
    """Identify and store device in database if not present."""
    init_db()
    session = get_session()
    device = session.query(Device).filter(Device.serial == serial).first()
    if device:
        session.close()
        return device

    # Determine mode
    mode = ""
    # Check if ADB
    try:
        adb_out = subprocess.check_output(["adb", "devices"], text=True, timeout=5)
        if serial in adb_out:
            mode = "ADB"
    except Exception:
        pass
    # Check if Fastboot
    if not mode:
        try:
            fb_out = subprocess.check_output(["fastboot", "devices"], text=True, timeout=5)
            if serial in fb_out:
                mode = "FASTBOOT"
        except Exception:
            pass

    if mode == "ADB":
        info = identify_adb(serial)
    elif mode == "FASTBOOT":
        info = identify_fastboot(serial)
    else:
        info = {"serial": serial, "mode": "USB", "model": "", "chipset": ""}

    device = Device(
        serial=serial,
        model=info.get("model", ""),
        chipset=info.get("chipset", ""),
        mode=info.get("mode", mode),
        status="connected"
    )
    session.add(device)
    session.commit()
    console.print(f"[green]New device stored: {serial} (Model: {device.model}, Chipset: {device.chipset}, Mode: {device.mode})[/green]")
    session.close()
    return device

def auto_flash(firmware_id: int = None, use_queue: bool = False):
    """Main loop to watch for devices and flash automatically."""
    console.print("[bold cyan]Auto-flash mode started. Watching for USB devices...[/bold cyan]")
    console.print("Press Ctrl+C to stop.\n")

    known_serials = get_connected_serials()
    console.print(f"Initially connected devices: {known_serials if known_serials else 'None'}")

    while True:
        try:
            current_serials = get_connected_serials()
            new_serials = current_serials - known_serials

            if new_serials:
                console.print(f"\n[bold yellow]New device(s) detected: {new_serials}[/bold yellow]")
                for serial in new_serials:
                    device = store_device(serial)

                    if firmware_id:
                        console.print(f"Flashing firmware ID {firmware_id} on {serial}...")
                        flash_device(serial, firmware_id)
                    elif use_queue:
                        # Look for queued jobs for this device
                        init_db()
                        session = get_session()
                        jobs = session.query(Job).filter(
                            Job.device_id == device.id,
                            Job.status == "queued"
                        ).all()
                        session.close()
                        if jobs:
                            console.print(f"Found {len(jobs)} queued job(s) for {serial}. Running them...")
                            for job in jobs:
                                _process_job(job.id)
                        else:
                            console.print(f"[yellow]No queued jobs for {serial}. Skipping.[/yellow]")
                    else:
                        console.print(f"[yellow]No automatic action configured for {serial}.[/yellow]")
                        console.print("Use --firmware-id or --use-queue to enable automatic flashing.")

                known_serials = current_serials
            else:
                # Also handle devices that were disconnected and reconnected
                # Update known_serials if devices disappeared
                known_serials = current_serials

            time.sleep(5)
        except KeyboardInterrupt:
            console.print("\n[bold]Auto-flash stopped.[/bold]")
            break
        except Exception as e:
            console.print(f"[red]Error in auto-flash loop: {e}[/red]")
            time.sleep(5)
