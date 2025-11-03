#!/usr/bin/env python3
from .log_converter import LogConverter
from .log_sender import LogSender
from .log_collector import LogCollector

class LogManager:
    """Основной менеджер для управления отправкой логов"""
    
    def __init__(self, log_callback=None):
        self.sender = LogSender(log_callback)
        self.collector = LogCollector(log_callback)
        self.is_sending = False
        self.log_callback = log_callback
    
    def log(self, message: str):
        """Логирование сообщений"""
        if self.log_callback:
            self.log_callback(message)
    
    def start_log_sending(self, config: dict, progress_callback=None):
        """Запуск автоматической отправки логов"""
        if self.is_sending:
            self.log("Отправка уже запущена")
            return False
        
        self.is_sending = True
        
        def sending_thread():
            file_count = config.get('file_count', 1)
            interval = config.get('send_interval', 60)
            logs_per_file = config.get('logs_per_file', 10)
            selected_systems = config.get('selected_systems', [])
            endpoint_url = config.get('endpoint_url', '')
            
            self.log(f"Запуск отправки {file_count} файлов")
            
            for i in range(file_count):
                if not self.is_sending:
                    break
                
                self.log(f"Отправка файла {i+1}/{file_count}...")
                
                # Создаем и отправляем файл
                log_file = self.collector.collect_real_logs(selected_systems, logs_per_file)
                if log_file:
                    # Для Suricata автоматически конвертируем в текст
                    convert_suricata = 'suricata' in selected_systems
                    success = self.sender.send_file_improved(log_file, endpoint_url, convert_suricata)
                    
                    # Очищаем временный файл
                    try:
                        import os
                        os.remove(log_file)
                    except:
                        pass
                
                # Обновляем прогресс
                if progress_callback:
                    progress_callback(i + 1, file_count)
                
                # Ждем перед следующей отправкой
                if i < file_count - 1 and self.is_sending:
                    import time
                    for sec in range(interval):
                        if not self.is_sending:
                            break
                        time.sleep(1)
                        if progress_callback:
                            progress_callback(i + 1, file_count, interval - sec)
            
            self.is_sending = False
            self.log("Автоматическая отправка завершена")
            if progress_callback:
                progress_callback(file_count, file_count, 0, completed=True)
        
        import threading
        thread = threading.Thread(target=sending_thread, daemon=True)
        thread.start()
        return True
    
    def stop_log_sending(self):
        """Остановка отправки логов"""
        self.is_sending = False
        self.log("Остановка отправки...")
    
    def send_test_file(self, endpoint_url: str, logs_per_file: int = 10) -> bool:
        """Отправка тестового файла"""
        self.log("Создание и отправка тестового файла...")
        
        test_file = self.collector.create_test_log_file(logs_per_file)
        if test_file:
            success = self.sender.send_file_improved(test_file, endpoint_url)
            # Удаляем временный файл
            try:
                import os
                os.remove(test_file)
            except:
                pass
            return success
        return False
    
    def test_connection(self, endpoint_url: str) -> bool:
        """Тестирование соединения с сервером"""
        return self.sender.test_server_connection(endpoint_url)
    
    def convert_suricata_logs(self, input_file: str, output_file: str = None) -> str:
        """Прямая конвертация файла Suricata"""
        converter = LogConverter(self.log_callback)
        return converter.convert_eve_to_text(input_file, output_file)
