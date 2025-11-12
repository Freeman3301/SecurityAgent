#!/usr/bin/env python3
import json
import os
import random
import psutil
import requests
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Callable

class LogCollector:
    """Унифицированный класс для сбора, конвертации и отправки логов"""
    
    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
        self.is_sending = False
    
    def log(self, message: str):
        if self.log_callback:
            self.log_callback(message)
    
    # === МЕТОДЫ СБОРА ЛОГОВ (из старого log_collector.py) ===
    def create_test_log_file(self, logs_per_file: int = 10) -> Optional[str]:
        # ... существующий код без изменений ...
    
    def collect_real_logs(self, selected_systems: List[str], logs_per_file: int = 10) -> Optional[str]:
        # ... существующий код без изменений ...
    
    def _get_suricata_logs(self) -> List[Dict]:
        # ... существующий код без изменений ...
    
    def _get_clamav_logs(self) -> List[Dict]:
        # ... существующий код без изменений ...
    
    def _generate_random_log(self, systems: List[str]) -> Dict:
        # ... существующий код без изменений ...
    
    # === МЕТОДЫ КОНВЕРТАЦИИ (из log_converter.py) ===
    def convert_eve_to_text(self, input_file: str, output_file: Optional[str] = None) -> Optional[str]:
        """Конвертация Suricata логов в текстовый формат"""
        if not os.path.exists(input_file):
            self.log(f"❌ Файл не найден: {input_file}")
            return None
        
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"/tmp/suricata_logs_{timestamp}.txt"
            
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            results = []
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    text_entry = self._format_suricata_entry(entry)
                    if text_entry:
                        results.append(text_entry)
                except json.JSONDecodeError:
                    continue
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(result + '\n\n')
            
            self.log(f"✅ Конвертировано {len(results)} записей: {output_file}")
            return output_file
            
        except Exception as e:
            self.log(f"❌ Ошибка конвертации: {e}")
            return None
    
    def _format_suricata_entry(self, entry):
        """Форматирование записи Suricata"""
        # Упрощенная версия форматирования
        timestamp = entry.get('timestamp', '')
        event_type = entry.get('event_type', 'unknown')
        
        if event_type == 'alert':
            alert = entry.get('alert', {})
            return f"[ALERT] {alert.get('signature', 'Unknown')} | {entry.get('src_ip', '')} -> {entry.get('dest_ip', '')}"
        elif event_type == 'http':
            http = entry.get('http', {})
            return f"[HTTP] {http.get('http_method', '')} {http.get('hostname', '')}{http.get('url', '')}"
        else:
            return f"[{event_type.upper()}] {entry.get('src_ip', '')} -> {entry.get('dest_ip', '')}"
    
    # === МЕТОДЫ ОТПРАВКИ (из log_sender.py) ===
    def send_file(self, file_path: str, url: str, convert_suricata: bool = True) -> bool:
        """Отправка файла на сервер"""
        if not os.path.exists(file_path):
            self.log(f"❌ Файл не найден: {file_path}")
            return False
        
        try:
            final_file_path = file_path
            if convert_suricata and ('suricata' in file_path.lower() or 'eve.json' in file_path):
                converted_file = self.convert_eve_to_text(file_path)
                if converted_file:
                    final_file_path = converted_file
            
            with open(final_file_path, 'rb') as f:
                files = {'file': (os.path.basename(final_file_path), f, 'text/plain')}
                response = requests.post(url, files=files, timeout=300)
                
                if response.status_code in [200, 201]:
                    self.log(f"✅ Файл отправлен: {os.path.basename(final_file_path)}")
                    
                    # Удаляем временный файл если он создавался
                    if final_file_path != file_path and os.path.exists(final_file_path):
                        os.remove(final_file_path)
                    
                    return True
                else:
                    self.log(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                    return False
                    
        except Exception as e:
            self.log(f"❌ Ошибка отправки: {e}")
            return False
    
    def test_connection(self, url: str) -> bool:
        """Тестирование соединения с сервером"""
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    # === МЕТОДЫ УПРАВЛЕНИЯ ОТПРАВКОЙ (из log_manager.py) ===
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
            
            for i in range(file_count):
                if not self.is_sending:
                    break
                
                log_file = self.collect_real_logs(selected_systems, logs_per_file)
                if log_file:
                    self.send_file(log_file, endpoint_url)
                    
                    # Очищаем временный файл
                    try:
                        os.remove(log_file)
                    except:
                        pass
                
                if progress_callback:
                    progress_callback(i + 1, file_count)
                
                if i < file_count - 1 and self.is_sending:
                    import time
                    for sec in range(interval):
                        if not self.is_sending:
                            break
                        time.sleep(1)
                        if progress_callback:
                            progress_callback(i + 1, file_count, interval - sec)
            
            self.is_sending = False
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
        test_file = self.create_test_log_file(logs_per_file)
        if test_file:
            success = self.send_file(test_file, endpoint_url)
            try:
                os.remove(test_file)
            except:
                pass
            return success
        return False
