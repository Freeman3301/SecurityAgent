#!/usr/bin/env python3
import tkinter as tk
from core.app import SecurityAgentApp

if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityAgentApp(root)
    root.mainloop()
