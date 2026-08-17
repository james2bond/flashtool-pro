import os
from rich.console import Console
from db.database import get_session, init_db
from db.models import Firmware, Device
from integrations import fastboot, samsung, mediatek, qualcomm, apple, laptop, nokia, motorola, huawei

console = Console()

def get_device_by_serial(serial):
    """Retrieve device record from DB."""
    init_db()
    session = get_session()
    device = session.query(Device).filter(Device.serial == serial).first()
    session.close()
    return device

def get_firmware_by_id(firmware_id):
    """Retrieve firmware record from DB."""
    init_db()
    session = get_session()
    fw = session.query(Firmware).filter(Firmware.id == firmware_id).first()
    session.close()
    return fw

def flash_device(serial, firmware_id):
    """Flash a device with the specified firmware."""
    device = get_device_by_serial(serial)
    firmware = get_firmware_by_id(firmware_id)

    if not device:
        console.print(f"[red]Device with serial {serial} not found in database.[/red]")
        console.print("[yellow]Run 'identify' first to add device to DB, or ensure device exists.[/yellow]")
        return False

    if not firmware:
        console.print(f"[red]Firmware ID {firmware_id} not found.[/red]")
        return False

    console.print(f"[bold cyan]Preparing to flash:[/bold cyan]")
    console.print(f"  Device: {device.model} ({device.serial})")
    console.print(f"  Firmware: {firmware.model} {firmware.version} ({firmware.source})")

    # Determine flashing method
    mode = device.mode.upper() if device.mode else ""
    chipset = device.chipset.lower() if device.chipset else ""
    model = device.model.lower() if device.model else ""
    manufacturer = device.manufacturer.lower() if device.manufacturer else ""

    firmware_path = firmware.file_path or firmware.url

    # Laptop
    if "laptop" in model or "notebook" in model or "thinkpad" in model or "macbook" in model:
        console.print("[cyan]Detected laptop. Using fwupd...[/cyan]")
        return laptop.flash_laptop(firmware_path)

    # Fastboot mode or brands that use fastboot
    if mode == "FASTBOOT" or any(brand in manufacturer for brand in ["nokia", "motorola", "huawei"]) or any(brand in model for brand in ["nokia", "motorola", "huawei"]):
        console.print("[cyan]Using fastboot method...[/cyan]")
        if "nokia" in manufacturer or "nokia" in model:
            return nokia.flash_nokia(serial, firmware_path)
        elif "motorola" in manufacturer or "motorola" in model:
            return motorola.flash_motorola(serial, firmware_path)
        elif "huawei" in manufacturer or "huawei" in model:
            return huawei.flash_huawei(serial, firmware_path)
        else:
            return fastboot.flash_fastboot(serial, firmware_path)

    # ADB mode
    elif mode == "ADB":
        console.print("[yellow]Device is in ADB mode. Need to reboot to bootloader/download mode first.[/yellow]")
        console.print("Please manually reboot the device to fastboot or download mode, then re-run flash.")
        return False

    # Samsung
    elif "samsung" in manufacturer or "samsung" in model or "exynos" in chipset or "sm" in chipset:
        console.print("[cyan]Using Samsung Heimdall method...[/cyan]")
        return samsung.flash_samsung(firmware_path)

    # MediaTek
    elif "mediatek" in chipset or "mtk" in chipset or "mt" in chipset:
        console.print("[cyan]Using MediaTek mtkclient method...[/cyan]")
        return mediatek.flash_mediatek(firmware_path)

    # Qualcomm EDL or Qualcomm chipset
    elif mode == "EDL" or "qualcomm" in chipset or "sm" in chipset or "msm" in chipset:
        console.print("[cyan]Using Qualcomm EDL method...[/cyan]")
        programmer = os.path.join(firmware_path, "prog_firehose.mbn") if os.path.isdir(firmware_path) else None
        return qualcomm.flash_qualcomm_edl(firmware_path, programmer)

    # Apple
    elif "iphone" in model or "ipad" in model or "apple" in manufacturer:
        console.print("[cyan]Using Apple idevicerestore method...[/cyan]")
        return apple.flash_apple(firmware_path)

    else:
        console.print(f"[red]No flashing method determined for mode={mode}, chipset={chipset}, model={model}.[/red]")
        console.print("[yellow]Ensure device is in correct mode (fastboot, download, EDL, DFU) and that chipset/manufacturer is recognized.[/yellow]")
        return False
