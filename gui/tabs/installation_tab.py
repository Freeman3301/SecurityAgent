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
        # Основной фрейм с сеткой
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Левая колонка - выбор систем
        left_frame = ttk.LabelFrame(main_frame, text="Выбор систем для установки")
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        ttk.Label(left_frame, text="Доступные системы безопасности:").pack(anchor='w', pady=5)
        
        self.systems_var = {}
        systems = [
            ("Suricata IDS/IPS", "suricata"),
            ("ClamAV Antivirus", "clamav"),
        ]
        
        for name, key in systems:
            var = tk.BooleanVar()
            self.systems_var[key] = var
            cb = ttk.Checkbutton(left_frame, text=name, variable=var)
            cb.pack(anchor='w', padx=10, pady=2)
        
        # Кнопки управления установкой
        install_btn_frame = ttk.Frame(left_frame)
        install_btn_frame.pack(fill='x', pady=10)
        
        ttk.Button(install_btn_frame, text="Установить выбранные системы",
                  command=self.install_systems).pack(fill='x', pady=2)
        
        ttk.Button(install_btn_frame, text="Проверить статус систем",
                  command=self.check_status).pack(fill='x', pady=2)
        
        # Правая колонка - индивидуальная установка
        right_frame = ttk.LabelFrame(main_frame, text="Индивидуальная установка")
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Выбор системы для детальной установки
        ttk.Label(right_frame, text="Система для детальной установки:").pack(anchor='w', pady=5)
        
        self.detail_system = tk.StringVar(value='suricata')
        system_combo = ttk.Combobox(right_frame, textvariable=self.detail_system, 
                                   values=['suricata', 'clamav'], state='readonly')
        system_combo.pack(fill='x', padx=5, pady=5)
        
        # Кнопки детальной установки
        detail_btn_frame = ttk.Frame(right_frame)
        detail_btn_frame.pack(fill='x', pady=5)
        
        ttk.Button(detail_btn_frame, text="Полная установка",
                  command=self.full_installation).pack(fill='x', pady=2)
        
        ttk.Button(detail_btn_frame, text="Только зависимости",
                  command=self.install_dependencies).pack(fill='x', pady=2)
        
        ttk.Button(detail_btn_frame, text="Только установка",
                  command=self.install_system_only).pack(fill='x', pady=2)
        
        ttk.Button(detail_btn_frame, text="Только настройка",
                  command=self.configure_system_only).pack(fill='x', pady=2)
        
        # Настройка весов сетки
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Лог установки
        log_frame = ttk.LabelFrame(self.frame, text="Лог установки")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.install_log = scrolledtext.ScrolledText(log_frame, height=12)
        self.install_log.pack(fill='both', expand=True, pady=5)
    
    def install_systems(self):
        """Установка выбранных систем"""
        selected = [key for key, var in self.systems_var.items() if var.get()]
        if not selected:
            messagebox.showwarning("Внимание", "Выберите системы для установки")
            return
            
        def install_thread():
            for system in selected:
                self.main_window.log_install(f"🚀 Начало установки {system.upper()}...")
                try:
                    result = self.main_window.logic.install_system(system)
                    self.main_window.log_install(f"{system.upper()}: {result}")
                except Exception as e:
                    self.main_window.log_install(f"❌ Ошибка установки {system}: {str(e)}")
                    
            self.main_window.log_install("✅ Установка завершена")
            
        threading.Thread(target=install_thread, daemon=True).start()
    
    def check_status(self):
        """Проверка статуса систем"""
        def status_thread():
            self.main_window.log_install("🔍 Проверка статуса систем...")
            for system in self.main_window.available_systems:
                status = self.main_window.logic.check_system_status(system)
                self.main_window.log_install(f"{system.upper()}: {status}")
            self.main_window.log_install("✅ Проверка завершена")
                
        threading.Thread(target=status_thread, daemon=True).start()
    
    def full_installation(self):
        """Полная установка выбранной системы"""
        system = self.detail_system.get()
        self.main_window.log_install(f"🚀 Запуск полной установки {system.upper()}...")
        
        def install_thread():
            result = self.main_window.logic.install_system(system)
            self.main_window.log_install(result)
            
        threading.Thread(target=install_thread, daemon=True).start()
    
    def install_dependencies(self):
        """Установка только зависимостей"""
        system = self.detail_system.get()
        self.main_window.log_install(f"📦 Установка зависимостей для {system.upper()}...")
        
        def install_thread():
            result = self.main_window.logic.install_dependencies(system)
            self.main_window.log_install(result)
            
        threading.Thread(target=install_thread, daemon=True).start()
    
    def install_system_only(self):
        """Установка только системы"""
        system = self.detail_system.get()
        self.main_window.log_install(f"⚙️ Установка {system.upper()}...")
        
        def install_thread():
            result = self.main_window.logic.install_security_system(system)
            self.main_window.log_install(result)
            
        threading.Thread(target=install_thread, daemon=True).start()
    
    def configure_system_only(self):
        """Настройка только системы"""
        system = self.detail_system.get()
        self.main_window.log_install(f"🔧 Настройка {system.upper()}...")
        
        def configure_thread():
            result = self.main_window.logic.configure_system(system)
            self.main_window.log_install(result)
            
        threading.Thread(target=configure_thread, daemon=True).start()
