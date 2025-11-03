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
        # Статус систем
        ttk.Label(self.frame, text="Статус установленных систем:").pack(pady=5)
        
        self.status_text = scrolledtext.ScrolledText(self.frame, height=15)
        self.status_text.pack(fill='both', expand=True, pady=5)
        
        # Кнопки обновления
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Обновить статус",
                  command=self.update_status).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Запустить все системы",
                  command=self.start_all_services).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Остановить все системы",
                  command=self.stop_all_services).pack(side='left', padx=5)
        
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
            selected_systems = [system for system, var in self.main_window.installation_tab.systems_var.items() if var.get()]
            if not selected_systems:
                messagebox.showwarning("Внимание", "Выберите системы для запуска")
                return
                
            for system in selected_systems:
                self.main_window.logic.start_service(system)
            self.update_status()
            messagebox.showinfo("Инфо", "Все службы запущены")
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def stop_all_services(self):
        """Остановка всех служб"""
        def stop_thread():
            selected_systems = [system for system, var in self.main_window.installation_tab.systems_var.items() if var.get()]
            if not selected_systems:
                messagebox.showwarning("Внимание", "Выберите системы для остановки")
                return
                
            self.main_window.log_install("Остановка всех служб...")
            for system in selected_systems:
                self.main_window.logic.stop_service(system)
            
            self.update_status()
            messagebox.showinfo("Инфо", "Все службы остановлены")
        
        threading.Thread(target=stop_thread, daemon=True).start()
