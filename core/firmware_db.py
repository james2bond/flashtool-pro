from rich.console import Console
from rich.table import Table

console = Console()

# Known official firmware URLs (placeholders; replace with actual official links)
KNOWN_FIRMWARE = [
    {
        "brand": "Google",
        "model": "Pixel 5",
        "version": "Android 13",
        "url": "https://developers.google.com/android/images#redfin",
        "source": "Google"
    },
    {
        "brand": "Google",
        "model": "Pixel 6",
        "version": "Android 14",
        "url": "https://developers.google.com/android/images#oriole",
        "source": "Google"
    },
    {
        "brand": "Samsung",
        "model": "Galaxy S21",
        "version": "Android 13",
        "url": "https://www.sammobile.com/firmwares/",
        "source": "Samsung"
    },
    {
        "brand": "Xiaomi",
        "model": "Redmi Note 10",
        "version": "MIUI 14",
        "url": "https://xiaomifirmwareupdater.com/",
        "source": "Xiaomi"
    },
    {
        "brand": "Motorola",
        "model": "Moto G Power",
        "version": "Android 12",
        "url": "https://motorola-global-portal.custhelp.com/app/standalone/bootloader/recovery-images",
        "source": "Motorola"
    },
    {
        "brand": "Nokia",
        "model": "Nokia G20",
        "version": "Android 12",
        "url": "https://www.nokia.com/phones/en_int/support/",
        "source": "Nokia"
    },
    {
        "brand": "Huawei",
        "model": "P30",
        "version": "EMUI 12",
        "url": "https://consumer.huawei.com/en/support/",
        "source": "Huawei"
    },
    {
        "brand": "Apple",
        "model": "iPhone 12",
        "version": "iOS 17",
        "url": "https://ipsw.me/",
        "source": "Apple"
    }
]

def search_known_firmware(brand: str = "", model: str = ""):
    """Search known firmware list."""
    results = []
    for fw in KNOWN_FIRMWARE:
        if brand and brand.lower() not in fw["brand"].lower():
            continue
        if model and model.lower() not in fw["model"].lower():
            continue
        results.append(fw)

    if not results:
        console.print("[yellow]No known firmware found. Check back later or add manually.[/yellow]")
        return results

    table = Table(title="Known Firmware URLs", show_header=True, header_style="bold green")
    table.add_column("Brand")
    table.add_column("Model")
    table.add_column("Version")
    table.add_column("URL")
    table.add_column("Source")
    for fw in results:
        table.add_row(fw["brand"], fw["model"], fw["version"], fw["url"], fw["source"])
    console.print(table)
    return results

import os
import requests
from rich import print
from rich.progress import Progress

def download_firmware(url, sha256, file_path):
    with Progress() as progress:
        task = progress.add_task("Downloading firmware", total=None)
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        progress.update(task, total=total_size)
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
        if sha256:
            import hashlib
            with open(file_path, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
                if checksum != sha256:
                    raise ValueError("SHA-256 checksum mismatch")
        return file_path
