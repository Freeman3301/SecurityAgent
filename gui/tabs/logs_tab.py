#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

class LogsTab:
    """Вкладка отправки логов"""
    
    def __init__(self, notebook, main_window):
        self.main_window = main_window
        self.frame = ttk.Frame(notebook)
        notebook.add(self.frame, text="Отправка логов")
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка интерфейса вкладки отправки логов"""
        # Конфигурация endpoint
        endpoint_frame = ttk.LabelFrame(self.frame, text="Конфигурация сервера")
        endpoint_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(endpoint_frame, text="URL endpoint сервера:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.endpoint_url = tk.StringVar(value=self.main_window.config.get('endpoint_url', 'http://10.8.0.5:8000/api/analyze_file'))
        ttk.Entry(endpoint_frame, textvariable=self.endpoint_url, width=50).grid(row=0, column=1, sticky='we', padx=5, pady=2)
        
        # Тестирование соединения
        test_frame = ttk.Frame(endpoint_frame)
        test_frame.grid(row=1, column=0, columnspan=2, sticky='we', pady=5)
        
        ttk.Button(test_frame, text="Проверить связь с сервером", 
                  command=self.test_server_connection).pack(side='left', padx=5)
        ttk.Button(test_frame, text="Отправить тестовый файл", 
                  command=self.send_test_file).pack(side='left', padx=5)
        
        # Настройки отправки
        settings_frame = ttk.LabelFrame(self.frame, text="Настройки отправки")
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Количество файлов
        ttk.Label(settings_frame, text="Количество файлов:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.file_count = tk.IntVar(value=self.main_window.config.get('file_count', 1))
        spinbox = ttk.Spinbox(settings_frame, from_=1, to=100, textvariable=self.file_count, width=10)
        spinbox.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        
        # Интервал отправки
        ttk.Label(settings_frame, text="Интервал (секунды):").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.send_interval = tk.IntVar(value=self.main_window.config.get('send_interval', 60))
        interval_spin = ttk.Spinbox(settings_frame, from_=5, to=3600, textvariable=self.send_interval, width=10)
        interval_spin.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        
        # Количество логов в файле
        ttk.Label(settings_frame, text="Логов в файле:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.logs_per_file = tk.IntVar(value=self.main_window.config.get('logs_per_file', 10))
        logs_spin = ttk.Spinbox(settings_frame, from_=1, to=1000, textvariable=self.logs_per_file, width=10)
        logs_spin.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        
        # Выбор систем для логов
        ttk.Label(settings_frame, text="Системы для логов:").grid(row=2, column=0, sticky='nw', padx=5, pady=2)
        systems_frame = ttk.Frame(settings_frame)
        systems_frame.grid(row=2, column=1, columnspan=3, sticky='we', padx=5, pady=2)
        
        self.log_systems_vars = {}
        log_systems = [
            ("Suricata", "suricata"),
            ("ClamAV", "clamav"),
            ("Системные ошибки", "system_errors")  # ЗАМЕНЕНО System на Системные ошибки
        ]
        
        for i, (name, key) in enumerate(log_systems):
            var = tk.BooleanVar(value=self.main_window.config.get(f'log_system_{key}', True))
            self.log_systems_vars[key] = var
            cb = ttk.Checkbutton(systems_frame, text=name, variable=var)
            cb.grid(row=0, column=i, sticky='w', padx=5)
        
        # Управление отправкой
        control_frame = ttk.LabelFrame(self.frame, text="Управление отправкой")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=5)
        
        self.start_send_btn = ttk.Button(btn_frame, text="Запустить отправку логов", 
                                       command=self.start_log_sending)
        self.start_send_btn.pack(side='left', padx=5)
        
        self.stop_send_btn = ttk.Button(btn_frame, text="Остановить отправку", 
                                      command=self.stop_log_sending, state='disabled')
        self.stop_send_btn.pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Сохранить настройки", 
                  command=self.save_log_settings).pack(side='left', padx=5)
        
        # Лог отправки
        log_frame = ttk.LabelFrame(self.frame, text="Лог отправки")
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.send_log = scrolledtext.ScrolledText(log_frame, height=15)
        self.send_log.pack(fill='both', expand=True, pady=5)
        
        # Статус бар
        self.send_status = ttk.Label(self.frame, text="Готов к работе", relief='sunken')
        self.send_status.pack(fill='x', padx=10, pady=5)
    
    def save_log_settings(self):
        """Сохранение настроек отправки логов"""
        self.main_window.config['endpoint_url'] = self.endpoint_url.get()
        self.main_window.config['file_count'] = self.file_count.get()
        self.main_window.config['send_interval'] = self.send_interval.get()
        self.main_window.config['logs_per_file'] = self.logs_per_file.get()
        
        for key, var in self.log_systems_vars.items():
            self.main_window.config[f'log_system_{key}'] = var.get()
        
        self.main_window.save_config()
        self.main_window.log_send("Настройки сохранены")
    
    def test_server_connection(self):
        """Тестирование соединения с сервером"""
        def test_thread():
            url = self.endpoint_url.get()
            self.main_window.log_send(f"Проверка соединения с {url}...")
            
            if self.main_window.log_collector.test_connection(url):  # ИЗМЕНЕНО: log_manager -> log_collector
                self.main_window.log_send("✅ Сервер доступен")
            else:
                self.main_window.log_send("❌ Сервер недоступен")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def send_test_file(self):
        """Отправка тестового файла"""
        def send_thread():
            url = self.endpoint_url.get()
            logs_per_file = self.logs_per_file.get()
            
            if self.main_window.log_collector.send_test_file(url, logs_per_file):  # ИЗМЕНЕНО: log_manager -> log_collector
                self.main_window.log_send("✅ Тестовый файл успешно отправлен")
            else:
                self.main_window.log_send("❌ Ошибка отправки тестового файла")
        
        threading.Thread(target=send_thread, daemon=True).start()
    
    def start_log_sending(self):
        """Запуск автоматической отправки логов"""
        config = {
            'file_count': self.file_count.get(),
            'send_interval': self.send_interval.get(),
            'logs_per_file': self.logs_per_file.get(),
            'selected_systems': [key for key, var in self.log_systems_vars.items() if var.get()],
            'endpoint_url': self.endpoint_url.get()
        }
        
        if self.main_window.log_collector.start_log_sending(config, self.update_progress):  # ИЗМЕНЕНО: log_manager -> log_collector
            self.start_send_btn.config(state='disabled')
            self.stop_send_btn.config(state='normal')
            self.send_status.config(text="Отправка логов активна")
    
    def stop_log_sending(self):
        """Остановка отправки логов"""
        self.main_window.log_collector.stop_log_sending()  # ИЗМЕНЕНО: log_manager -> log_collector
        self.start_send_btn.config(state='normal')
        self.stop_send_btn.config(state='disabled')
        self.send_status.config(text="Отправка остановлена")
    
    def update_progress(self, current: int, total: int, seconds_left: int = 0, completed: bool = False):
        """Обновление прогресса отправки"""
        def update_gui():
            if completed:
                self.send_status.config(text="Отправка завершена")
                self.start_send_btn.config(state='normal')
                self.stop_send_btn.config(state='disabled')
            elif seconds_left > 0:
                self.send_status.config(text=f"Отправка {current}/{total}. Следующий через {seconds_left} сек")
            else:
                self.send_status.config(text=f"Отправка {current}/{total}")
        
        self.main_window.root.after(0, update_gui)
