#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class InstallationTab:
    """Вкладка установки систем безопасности"""
    
    def __init__(self, notebook, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Установка систем")
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки установки"""
        ttk.Label(self.frame, text="Выберите системы для установки:").pack(pady=5)
        
        self.systems_var = {}
        systems = [
            ("Suricata IDS", "suricata"),
            ("ClamAV Antivirus", "clamav"),
            ("Fail2Ban", "fail2ban"),
            ("Auditd", "auditd"),
        ]
        
        for name, key in systems:
            var = tk.BooleanVar()
            self.systems_var[key] = var
            cb = ttk.Checkbutton(self.frame, text=name, variable=var)
            cb.pack(anchor='w', padx=20)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Установить выбранное",
                  command=self.install_systems).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Проверить статус",
                  command=self.check_status).pack(side='left', padx=5)
        
        # Лог установки
        self.install_log = scrolledtext.ScrolledText(self.frame, height=15)
        self.install_log.pack(fill='both', expand=True, pady=5)
    
    def install_systems(self):
        """Установка выбранных систем"""
        selected = [key for key, var in self.systems_var.items() if var.get()]
        if not selected:
            messagebox.showwarning("Внимание", "Выберите системы для установки")
            return
            
        def install_thread():
            for system in selected:
                self.main_window.log_install(f"Установка {system}...")
                try:
                    result = self.main_window.logic.install_system(system)
                    self.main_window.log_install(f"{system}: {result}")
                except Exception as e:
                    self.main_window.log_install(f"Ошибка установки {system}: {str(e)}")
                    
            self.main_window.log_install("Установка завершена")
            
        threading.Thread(target=install_thread, daemon=True).start()
    
    def check_status(self):
        """Проверка статуса систем"""
        def status_thread():
            self.main_window.log_install("Проверка статуса систем...")
            for system, var in self.systems_var.items():
                status = self.main_window.logic.check_system_status(system)
                self.main_window.log_install(f"{system}: {status}")
                
        threading.Thread(target=status_thread, daemon=True).start()
