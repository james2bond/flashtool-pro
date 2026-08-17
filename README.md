# FlashTool Pro

An authorized all-in-one firmware flashing and repair automation tool for phones, tablets, and laptops.

## Features
- Auto-detect connected devices (ADB, fastboot, USB)
- Identify model, chipset, and mode
- Firmware catalog with SHA-256 verification
- Flash official firmware for:
  - Google/Pixel/Xiaomi (fastboot)
  - Samsung (Heimdall)
  - MediaTek (mtkclient)
  - Qualcomm EDL (qdl)
  - Apple iPhone/iPad (idevicerestore)
  - Laptops (fwupd)
- Bulk flashing queue with parallel workers
- Self-learning firmware recommendations based on past outcomes
- Auto-flash mode when USB device is inserted
- Interactive built-in guide

## Requirements
- Python 3.10+
- ADB, fastboot, heimdall, mtkclient, qdl, idevicerestore, fwupd
- Linux environment recommended (or macOS with tools installed)

## Installation
```bash
git clone <your-repo-url>
cd flashtool-pro
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
