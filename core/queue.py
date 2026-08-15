import datetime
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.table import Table

from db.database import get_session, init_db
from db.models import Device, Firmware, Job, Outcome
from core.flash import flash_device

console = Console()

def add_job(serial: str, firmware_id: int, technician: str = "tech"):
    """Add a new flashing job to the queue."""
    init_db()
    session = get_session()

    # Check device exists
    device = session.query(Device).filter(Device.serial == serial).first()
    if not device:
        console.print(f"[red]Device with serial {serial} not found in database.[/red]")
        console.print("[yellow]Run 'identify' first to add device to DB, or add manually.[/yellow]")
        session.close()
        return False

    # Check firmware exists
    firmware = session.query(Firmware).filter(Firmware.id == firmware_id).first()
    if not firmware:
        console.print(f"[red]Firmware ID {firmware_id} not found.[/red]")
        session.close()
        return False

    # Create job
    job = Job(
        device_id=device.id,
        firmware_id=firmware.id,
        technician=technician,
        status="queued",
        logs="",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    session.add(job)
    session.commit()
    console.print(f"[green]Job added: {job.id} (Device: {device.serial}, Firmware: {firmware.model} {firmware.version})[/green]")
    session.close()
    return True

def list_jobs(status: str = ""):
    """List all jobs, optionally filtered by status."""
    init_db()
    session = get_session()
    query = session.query(Job).order_by(Job.created_at.desc())
    if status:
        query = query.filter(Job.status == status)
    jobs = query.all()

    if not jobs:
        console.print("[yellow]No jobs found.[/yellow]")
        session.close()
        return

    table = Table(title="Flashing Jobs", show_header=True, header_style="bold green")
    table.add_column("Job ID")
    table.add_column("Device")
    table.add_column("Firmware")
    table.add_column("Status")
    table.add_column("Technician")
    table.add_column("Created")

    for job in jobs:
        device = session.query(Device).filter(Device.id == job.device_id).first()
        firmware = session.query(Firmware).filter(Firmware.id == job.firmware_id).first()
        device_serial = device.serial if device else "?"
        fw_name = f"{firmware.model} {firmware.version}" if firmware else "?"
        table.add_row(
            str(job.id),
            device_serial,
            fw_name,
            job.status,
            job.technician,
            job.created_at.strftime("%Y-%m-%d %H:%M")
        )
    console.print(table)
    session.close()

def _process_job(job_id: int):
    """Worker function to process a single job."""
    init_db()
    session = get_session()
    job = session.query(Job).filter(Job.id == job_id).first()
    if not job:
        console.print(f"[red]Job {job_id} not found.[/red]")
        session.close()
        return

    device = session.query(Device).filter(Device.id == job.device_id).first()
    firmware = session.query(Firmware).filter(Firmware.id == job.firmware_id).first()
    if not device or not firmware:
        console.print(f"[red]Device or firmware missing for job {job_id}.[/red]")
        job.status = "failed"
        job.logs = "Device or firmware missing"
        session.commit()
        session.close()
        return

    console.print(f"[bold cyan]Starting job {job_id}: {device.serial} -> {firmware.model} {firmware.version}[/bold cyan]")
    job.status = "in_progress"
    session.commit()

    start_time = time.time()
    success = flash_device(device.serial, firmware.id)
    duration = int(time.time() - start_time)

    job.status = "success" if success else "failed"
    job.logs = f"Flashing completed with result: {job.status}"
    job.updated_at = datetime.datetime.utcnow()
    session.commit()

    # Record outcome
    outcome = Outcome(
        job_id=job.id,
        success=success,
        duration_secs=duration,
        error_log="" if success else "Flashing failed",
        ai_notes=""
    )
    session.add(outcome)
    session.commit()

    console.print(f"[bold green]Job {job_id} finished: {job.status} (took {duration}s)[/bold green]")
    session.close()

def run_queue(workers: int = 2):
    """Run all queued jobs in parallel using a thread pool."""
    init_db()
    session = get_session()
    queued_jobs = session.query(Job).filter(Job.status == "queued").all()
    session.close()

    if not queued_jobs:
        console.print("[yellow]No queued jobs to run.[/yellow]")
        return

    console.print(f"[bold cyan]Running {len(queued_jobs)} jobs with {workers} workers...[/bold cyan]")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_process_job, job.id): job.id for job in queued_jobs}
        for future in as_completed(futures):
            job_id = futures[future]
            try:
                future.result()
            except Exception as e:
                console.print(f"[red]Job {job_id} raised an exception: {e}[/red]")
