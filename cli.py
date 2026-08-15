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

@app.command()
def agent():
    """AI agent commands (placeholder)."""
    console.print("[bold green]AI agents...[/bold green]")
    console.print("[yellow]This is a placeholder. Will implement agents next.[/yellow]")

if __name__ == "__main__":
    app()
