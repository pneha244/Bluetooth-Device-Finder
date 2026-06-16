import asyncio
import json
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from bleak import BleakScanner, BleakError

SCAN_TIMEOUT = 10.0


class BluetoothDeviceFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Bluetooth Device Finder")
        self.root.geometry("820x620")
        self.devices = {}
        self.scan_thread = None

        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=16, pady=12)

        self.status_label = ttk.Label(top_frame, text="Ready to scan for Bluetooth devices.")
        self.status_label.pack(side="left", padx=(0, 12))

        scan_button = ttk.Button(top_frame, text="Start Scan", command=self.start_scan)
        scan_button.pack(side="right")

        refresh_button = ttk.Button(top_frame, text="Refresh Scan", command=self.start_scan)
        refresh_button.pack(side="right", padx=(0, 8))

        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=16)

        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=36)
        search_entry.pack(side="left", padx=(8, 8))
        search_entry.bind("<KeyRelease>", lambda event: self.filter_devices())

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=16, pady=12)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True)

        self.device_list = tk.Listbox(left_panel, height=24, activestyle="none")
        self.device_list.pack(fill="both", expand=True, side="left")
        self.device_list.bind("<<ListboxSelect>>", self.on_device_select)

        list_scroll = ttk.Scrollbar(left_panel, orient="vertical", command=self.device_list.yview)
        list_scroll.pack(side="right", fill="y")
        self.device_list.config(yscrollcommand=list_scroll.set)

        right_panel = ttk.Frame(main_frame, width=320)
        right_panel.pack(side="right", fill="y")

        ttk.Label(right_panel, text="Device Details", font=(None, 12, "bold")).pack(anchor="w", pady=(0, 8))
        self.details_text = tk.Text(right_panel, height=24, wrap="word", state="disabled", background="#f8f9fb")
        self.details_text.pack(fill="both", expand=True)

    def start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive():
            messagebox.showinfo("Scan in progress", "A scan is already running.")
            return

        self.status_label.config(text="Scanning for Bluetooth devices...")
        self.devices.clear()
        self.device_list.delete(0, tk.END)
        self.clear_details()
        self.scan_thread = threading.Thread(target=self.scan_devices, daemon=True)
        self.scan_thread.start()

    def scan_devices(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            devices = loop.run_until_complete(self.perform_scan())
            self.root.after(0, self.on_scan_complete, devices)
        except BleakError as exc:
            self.root.after(0, self.show_error, f"Bluetooth scan failed: {exc}")
        except Exception as exc:
            self.root.after(0, self.show_error, f"Unexpected error: {exc}")

    async def perform_scan(self):
        scanner = BleakScanner()
        found = await scanner.discover(timeout=SCAN_TIMEOUT)
        return found

    def on_scan_complete(self, found_devices):
        if not found_devices:
            self.status_label.config(text="No Bluetooth devices found.")
            return

        for device in found_devices:
            if device.address not in self.devices:
                self.devices[device.address] = {
                    "name": device.name or "Unknown",
                    "address": device.address,
                    "rssi": device.rssi,
                    "details": device.metadata,
                    "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            else:
                self.devices[device.address]["rssi"] = device.rssi
                self.devices[device.address]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.update_listbox()
        self.status_label.config(text=f"Scan complete: {len(self.devices)} unique device(s) found.")

    def update_listbox(self):
        self.device_list.delete(0, tk.END)
        query = self.search_var.get().strip().lower()
        for address, details in sorted(self.devices.items(), key=lambda item: item[1]["name"]):
            label = f"{details['name']} ({details['address']})"
            if query and query not in label.lower():
                continue
            self.device_list.insert(tk.END, label)

    def filter_devices(self):
        self.update_listbox()

    def on_device_select(self, event):
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        display_text = event.widget.get(index)
        address = display_text.split("(")[-1].rstrip(")")
        device = self.devices.get(address)
        if device:
            self.display_details(device)

    def display_details(self, device):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        lines = [
            f"Name: {device['name']}",
            f"Address: {device['address']}",
            f"RSSI: {device['rssi']}",
            f"Last Seen: {device['last_seen']}",
            "",
            "Metadata:",
            json.dumps(device['details'], indent=2) if device['details'] else "No extra metadata available."
        ]
        self.details_text.insert(tk.END, "\n".join(lines))
        self.details_text.config(state="disabled")

    def clear_details(self):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.config(state="disabled")

    def show_error(self, message):
        self.status_label.config(text=message)
        messagebox.showerror("Bluetooth Device Finder", message)


if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothDeviceFinder(root)
    root.mainloop()
