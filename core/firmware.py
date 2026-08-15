import hashlib
import os
import typer
from rich.console import Console
from rich.table import Table
from db.database import get_session, init_db
from db.models import Firmware

console = Console()

def verify_checksum(file_path: str, expected_sha256: str) -> bool:
    """Verify SHA-256 checksum of a file."""
    if not os.path.exists(file_path):
        console.print(f"[red]File not found: {file_path}[/red]")
        return False
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    actual = sha256_hash.hexdigest()
    if actual.lower() == expected_sha256.lower():
        console.print("[green]Checksum verified![/green]")
        return True
    else:
        console.print(f"[red]Checksum mismatch![/red]")
        console.print(f"Expected: {expected_sha256}")
        console.print(f"Actual:   {actual}")
        return False

def add_firmware(model: str, chipset: str, version: str, url: str, sha256: str, source: str, file_path: str = ""):
    """Add a firmware entry to the database."""
    init_db()
    session = get_session()
    fw = Firmware(
        model=model,
        chipset=chipset,
        version=version,
        url=url,
        sha256=sha256,
        source=source,
        file_path=file_path
    )
    session.add(fw)
    session.commit()
    console.print(f"[green]Firmware added: {model} {version} (ID: {fw.id})[/green]")
    session.close()

def list_firmwares():
    """List all firmware entries."""
    init_db()
    session = get_session()
    firmwares = session.query(Firmware).all()
    if not firmwares:
        console.print("[yellow]No firmware entries found.[/yellow]")
        session.close()
        return
    table = Table(title="Firmware Catalog", show_header=True, header_style="bold green")
    table.add_column("ID")
    table.add_column("Model")
    table.add_column("Chipset")
    table.add_column("Version")
    table.add_column("Source")
    for fw in firmwares:
        table.add_row(str(fw.id), fw.model, fw.chipset, fw.version, fw.source)
    console.print(table)
    session.close()

def search_firmware(model: str = "", chipset: str = ""):
    """Search firmware by model or chipset."""
    init_db()
    session = get_session()
    query = session.query(Firmware)
    if model:
        query = query.filter(Firmware.model.ilike(f"%{model}%"))
    if chipset:
        query = query.filter(Firmware.chipset.ilike(f"%{chipset}%"))
    results = query.all()
    if not results:
        console.print("[yellow]No matching firmware found.[/yellow]")
        session.close()
        return
    table = Table(title="Search Results", show_header=True, header_style="bold green")
    table.add_column("ID")
    table.add_column("Model")
    table.add_column("Chipset")
    table.add_column("Version")
    table.add_column("Source")
    for fw in results:
        table.add_row(str(fw.id), fw.model, fw.chipset, fw.version, fw.source)
    console.print(table)
    session.close()
