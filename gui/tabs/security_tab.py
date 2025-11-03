#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class SecurityTab:
    """Вкладка управления системами безопасности"""
    
    def __init__(self, notebook, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Управление системами")
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки безопасности"""
        # Основной фрейм с сеткой
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Левая колонка - управление системой
        left_frame = ttk.LabelFrame(main_frame, text="Управление выбранной системой")
        left_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Выбор системы
        ttk.Label(left_frame, text="Система:").pack(anchor='w', pady=5)
        system_combo = ttk.Combobox(left_frame, textvariable=self.main_window.current_system, 
                                   values=self.main_window.available_systems, state='readonly')
        system_combo.pack(fill='x', padx=5, pady=5)
        system_combo.bind('<<ComboboxSelected>>', self.on_system_changed)
        
        # Статус системы
        status_frame = ttk.Frame(left_frame)
        status_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(status_frame, text="Статус:").pack(side='left')
        self.status_label = ttk.Label(status_frame, text="Не проверен", foreground="orange")
        self.status_label.pack(side='left', padx=5)
        
        ttk.Button(status_frame, text="Проверить", 
                  command=self.check_current_status).pack(side='right')
        
        # Кнопки управления
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill='x', pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Запустить систему",
                                  command=self.start_system)
        self.start_btn.pack(fill='x', pady=2)
        
        self.stop_btn = ttk.Button(control_frame, text="Остановить систему",
                                 command=self.stop_system)
        self.stop_btn.pack(fill='x', pady=2)
        
        self.update_btn = ttk.Button(control_frame, text="Обновить правила/базу",
                                   command=self.update_system)
        self.update_btn.pack(fill='x', pady=2)
        
        # Правая колонка - информация о системе
        right_frame = ttk.LabelFrame(main_frame, text="Информация о системе")
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        info_text = """
Suricata - сетевая система обнаружения 
и предотвращения вторжений (IDS/IPS)

ClamAV - антивирусная система с открытым 
исходным кодом для сканирования файлов

Выберите систему для управления и мониторинга
"""
        ttk.Label(right_frame, text=info_text, justify='left').pack(anchor='w', padx=5, pady=5)
        
        # Настройка весов сетки
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Лог системы
        log_frame = ttk.LabelFrame(self.frame, text="Лог операций")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.system_log = scrolledtext.ScrolledText(log_frame, height=10)
        self.system_log.pack(fill='both', expand=True, pady=5)
        
        # Первоначальная проверка статуса
        self.check_current_status()
    
    def on_system_changed(self, event=None):
        """Обработчик изменения выбранной системы"""
        self.update_control_buttons()
        self.check_current_status()
        
    def update_control_buttons(self):
        """Обновление текста кнопок управления в зависимости от выбранной системы"""
        system = self.main_window.current_system.get()
        if system == 'suricata':
            self.update_btn.config(text="Обновить правила Suricata")
        elif system == 'clamav':
            self.update_btn.config(text="Обновить базу ClamAV")
    
    def check_current_status(self):
        """Проверка статуса текущей системы"""
        def status_thread():
            system = self.main_window.current_system.get()
            status = self.main_window.logic.check_system_status(system)
            
            def update_gui():
                self.status_label.config(text=status)
                if "✅" in status:
                    self.status_label.config(foreground="green")
                elif "❌" in status:
                    self.status_label.config(foreground="red")
                elif "⚠️" in status:
                    self.status_label.config(foreground="orange")
                else:
                    self.status_label.config(foreground="black")
            
            self.main_window.root.after(0, update_gui)
                
        threading.Thread(target=status_thread, daemon=True).start()
    
    def start_system(self):
        """Запуск выбранной системы"""
        system = self.main_window.current_system.get()
        
        def start_thread():
            self.main_window.log_system(f"🚀 Запуск {system.upper()}...")
            try:
                result = self.main_window.logic.start_system(system)
                self.main_window.log_system(result)
                # Обновляем статус после запуска
                self.check_current_status()
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение при запуске: {e}")
                
        threading.Thread(target=start_thread, daemon=True).start()

    def stop_system(self):
        """Остановка выбранной системы"""
        system = self.main_window.current_system.get()
        
        def stop_thread():
            self.main_window.log_system(f"🛑 Остановка {system.upper()}...")
            try:
                result = self.main_window.logic.stop_system(system)
                self.main_window.log_system(result)
                # Обновляем статус после остановки
                self.check_current_status()
            except Exception as e:
                self.main_window.log_system(f"❌ Ошибка остановки: {e}")
                
        threading.Thread(target=stop_thread, daemon=True).start()
    
    def update_system(self):
        """Обновление выбранной системы (правила/база)"""
        system = self.main_window.current_system.get()
        
        def update_thread():
            if system == 'suricata':
                self.main_window.log_system("🔄 Обновление правил Suricata...")
            elif system == 'clamav':
                self.main_window.log_system("🔄 Обновление базы данных ClamAV...")
                
            try:
                result = self.main_window.logic.update_system(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение: {str(e)}")
                
        threading.Thread(target=update_thread, daemon=True).start()
