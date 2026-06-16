import tkinter as tk
from app import BluetoothDeviceFinder


def test_application_initializes():
    root = tk.Tk()
    root.withdraw()
    app = BluetoothDeviceFinder(root)
    assert app.status_label.cget("text").startswith("Ready")
    root.destroy()


if __name__ == "__main__":
    test_application_initializes()
    print("Bluetooth Device Finder tests passed.")
