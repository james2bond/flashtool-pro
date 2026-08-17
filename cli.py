#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.table import Table

# Import detection and identification
from core.detect import detect_all
from core.identify import identify_all

# Import firmware management
from core.firmware import add_firmware, list_firmwares, search_firmware

# Import flashing
from core.flash import flash_device

# Import queue
from core.queue import add_job, list_jobs, run_queue

# Import self-learning
from core.self_learning import get_firmware_success_stats, display_firmware_stats, recommend_firmware

# Import auto-flash
from core.auto_flash import auto_flash

# Import guide (as guide_mod to avoid name conflict)
from core import guide as guide_mod

app = typer.Typer()
console = Console()

# ---------- Firmware command group ----------
firmware_app = typer.Typer(help="Manage firmware catalog")
app.add_typer(firmware_app, name="firmware")

@firmware_app.command("add")
def firmware_add(
    model: str = typer.Option(..., "--model", help="Device model"),
    chipset: str = typer.Option(..., "--chipset", help="Chipset name"),
    version: str = typer.Option(..., "--version", help="Firmware version"),
    url: str = typer.Option(..., "--url", help="Download URL"),
    sha256: str = typer.Option(..., "--sha256", help="SHA-256 checksum"),
    source: str = typer.Option("official", "--source", help="Source name"),
    file_path: str = typer.Option("", "--file-path", help="Local file path (optional)")
):
    """Add a new firmware entry."""
    add_firmware(model, chipset, version, url, sha256, source, file_path)

@firmware_app.command("list")
def firmware_list():
    """List all firmware entries."""
    list_firmwares()

@firmware_app.command("search")
def firmware_search(
    model: str = typer.Option("", "--model", help="Search by model"),
    chipset: str = typer.Option("", "--chipset", help="Search by chipset")
):
    """Search firmware by model or chipset."""
    search_firmware(model, chipset)

# ---------- Queue command group ----------
queue_app = typer.Typer(help="Manage flashing queue")
app.add_typer(queue_app, name="queue")

@queue_app.command("add")
def queue_add(
    serial: str = typer.Option(..., "--serial", "-s", help="Device serial"),
    firmware_id: int = typer.Option(..., "--firmware-id", "-f", help="Firmware ID"),
    technician: str = typer.Option("tech", "--technician", help="Technician name")
):
    """Add a job to the flashing queue."""
    add_job(serial, firmware_id, technician)

@queue_app.command("list")
def queue_list(
    status: str = typer.Option("", "--status", help="Filter by status (queued, in_progress, success, failed)")
):
    """List all jobs."""
    list_jobs(status)

@queue_app.command("run")
def queue_run(
    workers: int = typer.Option(2, "--workers", "-w", help="Number of parallel workers")
):
    """Run all queued jobs."""
    run_queue(workers)

# ---------- Self-Learning command group ----------
learn_app = typer.Typer(help="Self-learning and firmware recommendation")
app.add_typer(learn_app, name="learn")

@learn_app.command("stats")
def learn_stats(
    model: str = typer.Option("", "--model", help="Filter by device model"),
    chipset: str = typer.Option("", "--chipset", help="Filter by chipset")
):
    """Show firmware success statistics."""
    stats = get_firmware_success_stats(model, chipset)
    display_firmware_stats(stats)

@learn_app.command("recommend")
def learn_recommend(
    model: str = typer.Option("", "--model", help="Device model to recommend for"),
    chipset: str = typer.Option("", "--chipset", help="Chipset to recommend for")
):
    """Recommend the best firmware based on past outcomes."""
    recommend_firmware(model, chipset)

# ---------- Auto-Flash command ----------
@app.command()
def auto(
    firmware_id: int = typer.Option(None, "--firmware-id", "-f", help="Firmware ID to flash for all detected devices (optional)"),
    use_queue: bool = typer.Option(False, "--use-queue", help="Process queued jobs automatically when devices are detected")
):
    """Watch for USB devices and flash automatically."""
    auto_flash(firmware_id=firmware_id, use_queue=use_queue)

# ---------- Guide command ----------
@app.command()
def guide(
    device: str = typer.Option(None, "--device", "-d", help="Device type (fastboot, samsung, mediatek, qualcomm, apple, laptop)")
):
    """Show interactive guide or device-specific instructions."""
    if device is None:
        guide_mod.show_interactive_guide()
    elif device.lower() == "fastboot":
        guide_mod.show_fastboot_guide()
    elif device.lower() == "samsung":
        guide_mod.show_samsung_guide()
    elif device.lower() == "mediatek":
        guide_mod.show_mediatek_guide()
    elif device.lower() == "qualcomm":
        guide_mod.show_qualcomm_guide()
    elif device.lower() == "apple":
        guide_mod.show_apple_guide()
    elif device.lower() == "laptop":
        guide_mod.show_laptop_guide()
    else:
        console.print("[red]Unknown device type. Use one of: fastboot, samsung, mediatek, qualcomm, apple, laptop[/red]")

# ---------- Main commands ----------
@app.command()
def detect():
    """Detect connected devices."""
    detect_all()

@app.command()
def identify():
    """Identify device model and chipset."""
    identify_all()

@app.command()
def flash(
    serial: str = typer.Option(..., "--serial", "-s", help="Device serial"),
    firmware_id: int = typer.Option(..., "--firmware-id", "-f", help="Firmware ID from database")
):
    """Flash a single device directly."""
    flash_device(serial, firmware_id)

if __name__ == "__main__":
    app()
