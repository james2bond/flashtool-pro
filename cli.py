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

# Import AI agents
from agents.diagnose import diagnose_device
from agents.workflow import generate_workflow
from agents.qa import qa_job

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

# ---------- AI Agent command group ----------
agent_app = typer.Typer(help="AI agent commands")
app.add_typer(agent_app, name="agent")

@agent_app.command("diagnose")
def agent_diagnose(
    serial: str = typer.Option(..., "--serial", "-s", help="Device serial"),
    logs: str = typer.Option("", "--logs", help="Additional logs (optional)")
):
    """Run AI diagnostics on a device."""
    # Build device info from DB or basic string
    from db.database import get_session, init_db
    from db.models import Device
    init_db()
    session = get_session()
    device = session.query(Device).filter(Device.serial == serial).first()
    if device:
        device_info = f"Serial: {device.serial}, Model: {device.model}, Chipset: {device.chipset}, Mode: {device.mode}"
    else:
        device_info = f"Serial: {serial} (not found in database)"
    session.close()
    result = diagnose_device(device_info, logs)
    console.print(f"[bold green]AI Diagnosis:[/bold green]\n{result}")

@agent_app.command("workflow")
def agent_workflow(
    serial: str = typer.Option(..., "--serial", "-s", help="Device serial"),
    firmware_id: int = typer.Option(..., "--firmware-id", "-f", help="Firmware ID")
):
    """Generate a flashing workflow using AI."""
    from db.database import get_session, init_db
    from db.models import Device, Firmware
    init_db()
    session = get_session()
    device = session.query(Device).filter(Device.serial == serial).first()
    firmware = session.query(Firmware).filter(Firmware.id == firmware_id).first()
    if device and firmware:
        device_info = f"Serial: {device.serial}, Model: {device.model}, Chipset: {device.chipset}, Mode: {device.mode}"
        fw_info = f"Model: {firmware.model}, Version: {firmware.version}, Source: {firmware.source}"
    else:
        device_info = f"Serial: {serial}"
        fw_info = f"Firmware ID: {firmware_id}"
    session.close()
    result = generate_workflow(device_info, fw_info)
    console.print(f"[bold green]AI Workflow:[/bold green]\n{result}")

@agent_app.command("qa")
def agent_qa(
    job_id: int = typer.Option(..., "--job-id", help="Job ID to review")
):
    """Run AI quality assurance on a job."""
    from db.database import get_session, init_db
    from db.models import Job
    init_db()
    session = get_session()
    job = session.query(Job).filter(Job.id == job_id).first()
    if job:
        logs = job.logs or "No logs available"
    else:
        logs = f"Job {job_id} not found"
    session.close()
    result = qa_job(logs)
    console.print(f"[bold green]AI QA Result:[/bold green]\n{result}")

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
