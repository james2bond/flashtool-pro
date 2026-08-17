from rich.console import Console
from rich.markdown import Markdown
import typer

console = Console()

GUIDE_MAIN = """
# FlashTool Pro - Interactive Guide

Welcome! This guide will help you use the tool for authorized firmware flashing and device servicing.

**Choose a topic to learn more:**
1. Getting Started
2. Fastboot flashing (Google, Pixel, Xiaomi)
3. Samsung flashing (Heimdall)
4. MediaTek flashing (mtkclient)
5. Qualcomm EDL flashing (qdl)
6. Apple iPhone/iPad restore (idevicerestore)
7. Laptop firmware update (fwupd)
8. Bulk queue and self-learning
9. Exit guide
"""

GUIDE_GETTING_STARTED = """
# Getting Started

## Basic Workflow
1. **Detect devices**   : `python cli.py detect`
2. **Identify device**  : `python cli.py identify`
3. **Add firmware**     : `python cli.py firmware add --model "Pixel 5" --chipset "sm7250" --version "Android 13" --url "https://..." --sha256 "abc123" --source "Google"`
4. **Flash manually**   : `python cli.py flash --serial <serial> --firmware-id <id>`
5. **Auto-flash mode**  : `python cli.py auto --firmware-id <id>` (flashes any new device automatically)

## Key Commands
- `detect`              : List connected devices (ADB, fastboot, USB)
- `identify`            : Identify model/chipset and store in database
- `firmware add/list/search` : Manage firmware catalog
- `queue add/list/run`  : Bulk flashing queue
- `learn stats/recommend` : Self-learning system
- `auto`                : Watch for USB insertion and flash automatically
- `guide`               : Show interactive guide

## Important Notes
- Only use **official firmware** from trusted sources.
- Verify SHA-256 checksum before flashing.
- Ensure battery level > 50% for phones.
- Always back up data before flashing.
- Do not disconnect device during flashing.
"""

GUIDE_FASTBOOT = """
# Fastboot Flashing Guide

## Prerequisites
- Device with unlocked bootloader (if required)
- Official fastboot ROM images (boot.img, system.img, vendor.img, etc.)
- Platform tools installed (adb, fastboot)

## Steps
1. Power off the device.
2. Boot into fastboot mode:
   - Pixel: Hold Volume Down + Power
   - Xiaomi: Hold Volume Down + Power
3. Connect USB cable.
4. Verify device detected:
   `fastboot devices`
5. Flash each partition:
6. Reboot:
`fastboot reboot`

## Troubleshooting
- "Waiting for device" → Check USB driver/connection.
- "FAILED (remote: 'locked')" → Bootloader is locked; unlock it first (if allowed).
- Always use correct firmware for the exact model.
"""

GUIDE_SAMSUNG = """
# Samsung Flashing Guide (Heimdall)

## Prerequisites
- Samsung device in Download mode
- Official Samsung firmware files (boot.img, system.img, recovery.img, etc.)
- Heimdall installed

## Steps
1. Power off the device.
2. Boot into Download mode:
- Hold Volume Down + Home + Power (older)
- Hold Volume Down + Bixby + Power (newer)
3. Connect USB cable.
4. Verify device detected:
`heimdall detect`
5. Flash:

6. Reboot:
`heimdall reboot`

## Important
- Use only official Samsung firmware.
- Do not interrupt the flashing process.
"""

GUIDE_MEDIATEK = """
# MediaTek Flashing Guide (mtkclient)

## Prerequisites
- MediaTek device (preloader mode or brom)
- Official firmware images
- mtkclient installed

## Steps
1. Power off the device.
2. Connect USB cable while holding Volume Up (or use test point).
3. Device should be detected in PreLoader or BROM mode.
4. Run mtkclient to flash:
5. Reset device:
`mtkclient reset`

## Note
- Use correct scatter file if provided by OEM.
- Never disconnect during flashing.
"""

GUIDE_QUALCOMM = """
# Qualcomm EDL Flashing Guide (qdl)

## Prerequisites
- Device in EDL mode (Qualcomm emergency download)
- Firehose programmer (prog_firehose.mbn)
- Rawprogram XML and patch XML files
- qdl installed

## Steps
1. Boot device into EDL mode (often via key combo or test point).
2. Connect USB cable.
3. Run:
4. Wait for flashing to complete and device to reboot.

## Important
- Use the correct programmer for your SoC (e.g., SDM845, SM8150).
- EDL mode is low-level; be cautious.
"""

GUIDE_APPLE = """
# Apple iPhone/iPad Restore Guide

## Prerequisites
- Apple device in DFU or Recovery mode
- Official IPSW firmware file
- idevicerestore installed

## Steps
1. Connect device to computer.
2. Enter DFU/Recovery mode:
- iPhone 8+ : Press Volume Up, Volume Down, then hold Side button until recovery.
- iPad with Face ID : Press Volume Up, Volume Down, hold Top button.
3. Verify detected:
`ideviceinfo`
4. Restore:
`idevicerestore <path-to.ipsw>`
5. Wait for process to finish.

## Note
- This will erase all data (if using erase mode).
- Use official IPSW from Apple.
"""

GUIDE_LAPTOP = """
# Laptop Firmware Update Guide (fwupd)

## Prerequisites
- Laptop with fwupd support
- fwupd installed

## Steps
1. Ensure laptop is connected to power.
2. Refresh metadata:
`fwupdmgr refresh`
3. Check available updates:
`fwupdmgr get-updates`
4. Apply updates:
`fwupdmgr update`

## Note
- Some updates require reboot.
- Keep laptop plugged in during update.
"""

GUIDE_QUEUE = """
# Bulk Queue and Self-Learning

## Bulk Flashing
1. Add a job:
`python cli.py queue add --serial <serial> --firmware-id <id> --technician "John"`
2. List jobs:
`python cli.py queue list`
3. Run queue:
`python cli.py queue run --workers 2`

## Self-Learning
The tool automatically records outcomes and recommends the best firmware.

- View stats:
`python cli.py learn stats`
- Get recommendation:
`python cli.py learn recommend --model "Pixel 5"`
"""

def show_main_guide():
 """Display the main guide."""
 console.print(Markdown(GUIDE_MAIN))

def show_interactive_guide():
 """Interactive menu for guides."""
 while True:
     console.print(Markdown(GUIDE_MAIN))
     choice = typer.prompt("Enter a number (1-9) or 'q' to quit", default="1")
     choice = choice.strip().lower()
     if choice == 'q' or choice == 'quit':
         console.print("[bold]Exiting guide. Good luck![/bold]")
         break
     elif choice == '1':
         console.print(Markdown(GUIDE_GETTING_STARTED))
     elif choice == '2':
         console.print(Markdown(GUIDE_FASTBOOT))
     elif choice == '3':
         console.print(Markdown(GUIDE_SAMSUNG))
     elif choice == '4':
         console.print(Markdown(GUIDE_MEDIATEK))
     elif choice == '5':
         console.print(Markdown(GUIDE_QUALCOMM))
     elif choice == '6':
         console.print(Markdown(GUIDE_APPLE))
     elif choice == '7':
         console.print(Markdown(GUIDE_LAPTOP))
     elif choice == '8':
         console.print(Markdown(GUIDE_QUEUE))
     elif choice == '9':
         console.print("[bold]Exiting guide. Good luck![/bold]")
         break
     else:
         console.print("[red]Invalid choice. Please enter a number between 1 and 9, or 'q'.[/red]")
     input("\nPress Enter to continue...")
     # Clear screen (optional)
     # os.system('clear' if os.name == 'posix' else 'cls')

# Standalone functions for CLI if needed (keeping backward compatibility)
def show_fastboot_guide():
 console.print(Markdown(GUIDE_FASTBOOT))

def show_samsung_guide():
 console.print(Markdown(GUIDE_SAMSUNG))

def show_mediatek_guide():
 console.print(Markdown(GUIDE_MEDIATEK))

def show_qualcomm_guide():
 console.print(Markdown(GUIDE_QUALCOMM))

def show_apple_guide():
 console.print(Markdown(GUIDE_APPLE))

def show_laptop_guide():
 console.print(Markdown(GUIDE_LAPTOP))
