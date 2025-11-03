#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class SecurityTab:
    """Вкладка настройки систем безопасности"""
    
    def __init__(self, notebook, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Настройка систем")
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки безопасности"""
        # Выбор системы
        system_frame = ttk.LabelFrame(self.frame, text="Выбор системы безопасности")
        system_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(system_frame, text="Система:").pack(side='left', padx=5)
        system_combo = ttk.Combobox(system_frame, textvariable=self.main_window.current_system, 
                                   values=['suricata', 'clamav'], state='readonly')
        system_combo.pack(side='left', padx=5)
        system_combo.bind('<<ComboboxSelected>>', self.on_system_changed)
        
        # Установка системы
        install_frame = ttk.LabelFrame(self.frame, text="Установка и настройка")
        install_frame.pack(fill='x', padx=10, pady=5)
        
        install_btn_frame = ttk.Frame(install_frame)
        install_btn_frame.pack(pady=5)
        
        ttk.Button(install_btn_frame, text="Установить зависимости",
                  command=self.install_dependencies).pack(side='left', padx=5)
        ttk.Button(install_btn_frame, text="Установить систему",
                  command=self.install_security_system).pack(side='left', padx=5)
        ttk.Button(install_btn_frame, text="Настроить систему",
                  command=self.configure_system).pack(side='left', padx=5)
        
        # Управление системой
        control_frame = ttk.LabelFrame(self.frame, text="Управление системой")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        control_btn_frame = ttk.Frame(control_frame)
        control_btn_frame.pack(pady=5)
        
        self.start_btn = ttk.Button(control_btn_frame, text="Запустить систему",
                                  command=self.start_system)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(control_btn_frame, text="Остановить систему",
                                 command=self.stop_system)
        self.stop_btn.pack(side='left', padx=5)
        
        self.update_btn = ttk.Button(control_btn_frame, text="Обновить правила",
                                   command=self.update_system)
        self.update_btn.pack(side='left', padx=5)
        
        # Обновляем текст кнопок при изменении системы
        self.update_control_buttons()
        
        # Лог системы
        self.system_log = scrolledtext.ScrolledText(self.frame, height=12)
        self.system_log.pack(fill='both', expand=True, pady=5)
    
    def on_system_changed(self, event=None):
        """Обработчик изменения выбранной системы"""
        self.update_control_buttons()
        
    def update_control_buttons(self):
        """Обновление текста кнопок управления в зависимости от выбранной системы"""
        system = self.main_window.current_system.get()
        if system == 'suricata':
            self.update_btn.config(text="Обновить правила")
        elif system == 'clamav':
            self.update_btn.config(text="Обновить базу данных")
    
    def install_dependencies(self):
        """Установка зависимостей для выбранной системы"""
        system = self.main_window.current_system.get()
        
        def install_thread():
            self.main_window.log_system(f"Установка зависимостей для {system}...")
            try:
                result = self.main_window.logic.install_dependencies(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение: {str(e)}")
                
        threading.Thread(target=install_thread, daemon=True).start()
    
    def install_security_system(self):
        """Установка выбранной системы безопасности"""
        system = self.main_window.current_system.get()
        
        def install_thread():
            self.main_window.log_system(f"Установка {system}...")
            try:
                result = self.main_window.logic.install_security_system(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение: {str(e)}")
                
        threading.Thread(target=install_thread, daemon=True).start()
    
    def configure_system(self):
        """Настройка выбранной системы"""
        system = self.main_window.current_system.get()
        
        def configure_thread():
            self.main_window.log_system(f"Настройка {system}...")
            try:
                result = self.main_window.logic.configure_system(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение: {str(e)}")
                
        threading.Thread(target=configure_thread, daemon=True).start()
    
    def start_system(self):
        """Запуск выбранной системы"""
        system = self.main_window.current_system.get()
        
        def start_thread():
            self.main_window.log_system(f"Запуск {system}...")
            try:
                result = self.main_window.logic.start_system(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение при запуске: {e}")
                
        threading.Thread(target=start_thread, daemon=True).start()

    def stop_system(self):
        """Остановка выбранной системы"""
        system = self.main_window.current_system.get()
        
        def stop_thread():
            self.main_window.log_system(f"Остановка {system}...")
            try:
                result = self.main_window.logic.stop_system(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Ошибка остановки: {e}")
                
        threading.Thread(target=stop_thread, daemon=True).start()
    
    def update_system(self):
        """Обновление выбранной системы (правила/база)"""
        system = self.main_window.current_system.get()
        
        def update_thread():
            if system == 'suricata':
                self.main_window.log_system("Обновление правил Suricata...")
            elif system == 'clamav':
                self.main_window.log_system("Обновление базы данных ClamAV...")
                
            try:
                result = self.main_window.logic.update_system(system)
                self.main_window.log_system(result)
            except Exception as e:
                self.main_window.log_system(f"❌ Исключение: {str(e)}")
                
        threading.Thread(target=update_thread, daemon=True).start()
