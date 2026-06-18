# Bluetooth Device Finder

A Python application that discovers nearby Bluetooth devices, lists unique devices, and displays device details.

## Features
- Detects available Bluetooth adapters
- Scans nearby Bluetooth devices
- Displays device name, MAC address, RSSI, and metadata
- Supports device search by name or address
- Refresh scan to discover devices again
- Handles duplicate devices and updates information

## Setup
1. Create and activate a Python virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Notes
- Bluetooth adapter support depends on the platform and hardware.
- The app uses `bleak` for cross-platform Bluetooth scanning.
- On Windows, Bluetooth permission and adapter support are required.

## Authors

Developed by Neha P
