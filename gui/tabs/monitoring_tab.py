#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class MonitoringTab:
    """Вкладка мониторинга систем"""
    
    def __init__(self, notebook, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Мониторинг")
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки мониторинга"""
        # Основной фрейм с сеткой
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Левая колонка - статус систем
        status_frame = ttk.LabelFrame(main_frame, text="Статус систем безопасности")
        status_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=15)
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Правая колонка - управление
        control_frame = ttk.LabelFrame(main_frame, text="Управление системами")
        control_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Кнопки управления
        ttk.Button(control_frame, text="Обновить статус",
                  command=self.update_status).pack(fill='x', pady=5, padx=5)
        
        ttk.Button(control_frame, text="Запустить все системы",
                  command=self.start_all_services).pack(fill='x', pady=5, padx=5)
        
        ttk.Button(control_frame, text="Остановить все системы",
                  command=self.stop_all_services).pack(fill='x', pady=5, padx=5)
        
        ttk.Button(control_frame, text="Обновить все правила/базы",
                  command=self.update_all_systems).pack(fill='x', pady=5, padx=5)
        
        # Информация о системах
        info_frame = ttk.LabelFrame(control_frame, text="Информация")
        info_frame.pack(fill='x', pady=10, padx=5)
        
        info_text = """
Suricata: сетевая защита
ClamAV: антивирусная защита

Используйте кнопки для управления
всеми системами одновременно
"""
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w', padx=5, pady=5)
        
        # Настройка весов сетки
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Первоначальное обновление статуса
        self.update_status()
    
    def update_status(self):
        """Обновление статуса в мониторинге"""
        def status_thread():
            status_info = self.main_window.logic.get_system_status_info()
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, status_info)
            
        threading.Thread(target=status_thread, daemon=True).start()
    
    def start_all_services(self):
        """Запуск всех служб"""
        def start_thread():
            self.main_window.log_install("🚀 Запуск всех систем безопасности...")
            for system in self.main_window.available_systems:
                self.main_window.log_install(f"Запуск {system}...")
                self.main_window.logic.start_service(system)
            
            self.update_status()
            self.main_window.log_install("✅ Все системы запущены")
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_all_services(self):
        """Остановка всех служб"""
        def stop_thread():
            self.main_window.log_install("🛑 Остановка всех систем безопасности...")
            for system in self.main_window.available_systems:
                self.main_window.log_install(f"Остановка {system}...")
                self.main_window.logic.stop_service(system)
            
            self.update_status()
            self.main_window.log_install("✅ Все системы остановлены")
        
        threading.Thread(target=stop_thread, daemon=True).start()
    
    def update_all_systems(self):
        """Обновление всех систем"""
        def update_thread():
            self.main_window.log_install("🔄 Обновление всех систем...")
            for system in self.main_window.available_systems:
                self.main_window.log_install(f"Обновление {system}...")
                self.main_window.logic.update_system(system)
            
            self.update_status()
            self.main_window.log_install("✅ Все системы обновлены")
        
        threading.Thread(target=update_thread, daemon=True).start()
