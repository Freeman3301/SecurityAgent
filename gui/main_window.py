#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from pathlib import Path
from datetime import datetime

from services.log_manager import LogManager
from .tabs.installation_tab import InstallationTab
from .tabs.security_tab import SecurityTab
from .tabs.monitoring_tab import MonitoringTab
from .tabs.logs_tab import LogsTab

class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, root, logic):
        self.root = root
        self.logic = logic
        self.root.title("System Security Agent v1.0 - Suricata & ClamAV")
        self.root.geometry("1000x800")
        
        # Конфигурация
        self.config_file = Path.home() / '.system_agent_config.json'
        self.load_config()
        
        # Менеджер логов
        self.log_manager = LogManager(self.log_send)
        
        # Текущая выбранная система
        self.current_system = tk.StringVar(value='suricata')
        
        # Доступные системы
        self.available_systems = ['suricata', 'clamav']
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Создаем вкладки
        self.installation_tab = InstallationTab(notebook, self)
        self.security_tab = SecurityTab(notebook, self)
        self.monitoring_tab = MonitoringTab(notebook, self)
        self.logs_tab = LogsTab(notebook, self)
    
    # === ЛОГГИРОВАНИЕ ===
    
    def log_install(self, message):
        """Логирование для вкладки установки"""
        def update_gui():
            self.installation_tab.install_log.insert(tk.END, f"{self.get_timestamp()} - {message}\n")
            self.installation_tab.install_log.see(tk.END)
            
        self.root.after(0, update_gui)
    
    def log_system(self, message):
        """Логирование для вкладки систем безопасности"""
        def update_gui():
            self.security_tab.system_log.insert(tk.END, f"{self.get_timestamp()} - {message}\n")
            self.security_tab.system_log.see(tk.END)
            
        self.root.after(0, update_gui)
    
    def log_send(self, message):
        """Логирование для вкладки отправки"""
        def update_gui():
            self.logs_tab.send_log.insert(tk.END, f"{self.get_timestamp()} - {message}\n")
            self.logs_tab.send_log.see(tk.END)
            
        self.root.after(0, update_gui)
    
    def get_timestamp(self):
        """Получение временной метки"""
        return datetime.now().strftime('%H:%M:%S')

    # === КОНФИГУРАЦИЯ ===
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {}
    
    def save_config(self):
        """Сохранение конфигурации"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
