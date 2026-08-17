from sqlalchemy import func
from rich.console import Console
from rich.table import Table

from db.database import get_session, init_db
from db.models import Device, Firmware, Job, Outcome

console = Console()

def get_firmware_success_stats(model: str = "", chipset: str = ""):
    """Return success statistics for firmware, optionally filtered by device model/chipset."""
    init_db()
    session = get_session()

    query = (
        session.query(
            Firmware.id,
            Firmware.model,
            Firmware.version,
            Firmware.source,
            func.count(Outcome.id).label("total_attempts"),
            func.sum(Outcome.success).label("successes")
        )
        .join(Job, Job.firmware_id == Firmware.id)
        .join(Outcome, Outcome.job_id == Job.id)
        .join(Device, Device.id == Job.device_id)
    )

    if model:
        query = query.filter(Device.model.ilike(f"%{model}%"))
    if chipset:
        query = query.filter(Device.chipset.ilike(f"%{chipset}%"))

    query = query.group_by(Firmware.id)
    results = query.all()
    session.close()
    return results

def display_firmware_stats(stats):
    """Print firmware success statistics as a table."""
    if not stats:
        console.print("[yellow]No outcome data available yet. Flash some devices first to build history.[/yellow]")
        return

    table = Table(title="Firmware Success Statistics", show_header=True, header_style="bold green")
    table.add_column("Firmware ID")
    table.add_column("Model")
    table.add_column("Version")
    table.add_column("Source")
    table.add_column("Attempts")
    table.add_column("Successes")
    table.add_column("Rate")
    for s in stats:
        rate = (s.successes / s.total_attempts * 100) if s.total_attempts and s.total_attempts > 0 else 0
        table.add_row(
            str(s.id),
            s.model,
            s.version,
            s.source,
            str(s.total_attempts),
            str(s.successes),
            f"{rate:.1f}%"
        )
    console.print(table)

def get_best_firmware(model: str = "", chipset: str = ""):
    """Return the best firmware based on success rate and source priority, without printing."""
    stats = get_firmware_success_stats(model, chipset)
    if not stats:
        return None
    # Sort by success rate desc, official source first, total attempts desc
    stats_sorted = sorted(
        stats,
        key=lambda x: (
            (x.successes / x.total_attempts if x.total_attempts and x.total_attempts > 0 else 0),
            1 if x.source.lower() == "official" else 0,
            x.total_attempts
        ),
        reverse=True
    )
    return stats_sorted[0]

def recommend_firmware(model: str = "", chipset: str = ""):
    """Recommend the best firmware based on past success rates (prints detailed stats)."""
    stats = get_firmware_success_stats(model, chipset)
    if not stats:
        console.print("[yellow]No outcome data available yet. Flash some devices first to build history.[/yellow]")
        return None

    best = get_best_firmware(model, chipset)
    if best is None:
        console.print("[yellow]No recommendation available.[/yellow]")
        return None

    success_rate = (best.successes / best.total_attempts * 100) if best.total_attempts > 0 else 0

    console.print("[bold green]Recommended Firmware:[/bold green]")
    console.print(f"  Model: {best.model}")
    console.print(f"  Version: {best.version}")
    console.print(f"  Source: {best.source}")
    console.print(f"  Success Rate: {success_rate:.1f}% ({best.successes}/{best.total_attempts})")

    display_firmware_stats(stats)
    return best
