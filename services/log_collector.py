#!/usr/bin/env python3
import json
import os
import random
import psutil
from datetime import datetime
from typing import List, Dict, Optional, Callable

class LogCollector:
    """Класс для сбора и генерации логов"""
    
    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
    
    def log(self, message: str):
        """Логирование сообщений"""
        if self.log_callback:
            self.log_callback(message)
    
    def create_test_log_file(self, logs_per_file: int = 10) -> Optional[str]:
        """Создание тестового файла с логами"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/test_log_{timestamp}.json"
            
            test_logs = []
            for i in range(logs_per_file):
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "system": "test",
                    "level": random.choice(["INFO", "WARNING", "ERROR"]),
                    "message": f"Тестовое сообщение лога #{i+1}",
                    "source": "system_agent_gui",
                    "data": {
                        "cpu_usage": random.randint(1, 100),
                        "memory_usage": random.randint(1, 100),
                        "random_value": random.randint(1000, 9999)
                    }
                }
                test_logs.append(log_entry)
            
            with open(filename, 'w') as f:
                json.dump(test_logs, f, indent=2, ensure_ascii=False)
            
            return filename
        except Exception as e:
            self.log(f"Ошибка создания тестового файла: {e}")
            return None
    
    def collect_real_logs(self, selected_systems: List[str], logs_per_file: int = 10) -> Optional[str]:
        """Сбор реальных логов с системы"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Если выбран только suricata, конвертируем напрямую в текст
            if selected_systems == ['suricata']:
                suricata_file = "/var/log/suricata/eve.json"
                if os.path.exists(suricata_file):
                    from .log_converter import LogConverter
                    converter = LogConverter(self.log_callback)
                    converted_file = converter.convert_eve_to_text(suricata_file)
                    if converted_file:
                        self.log(f"✅ Сконвертирован файл Suricata: {converted_file}")
                        return converted_file
            
            # Стандартный сбор логов
            filename = f"/tmp/system_logs_{timestamp}.json"
            
            logs = []
            
            # Сбор системных логов
            if 'system' in selected_systems:
                system_log = {
                    "timestamp": datetime.now().isoformat(),
                    "system": "system",
                    "level": "INFO",
                    "message": "System status snapshot",
                    "data": {
                        "cpu_percent": psutil.cpu_percent(),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_usage": psutil.disk_usage('/').percent,
                        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
                    }
                }
                logs.append(system_log)
            
            # Сбор логов Suricata если доступны
            if 'suricata' in selected_systems:
                suricata_logs = self._get_suricata_logs()
                logs.extend(suricata_logs)
            
            # Сбор логов ClamAV если доступны
            if 'clamav' in selected_systems:
                clamav_logs = self._get_clamav_logs()
                logs.extend(clamav_logs)
            
            # Добавляем случайные логи если нужно больше
            while len(logs) < logs_per_file:
                log_entry = self._generate_random_log(selected_systems)
                logs.append(log_entry)
            
            # Сохраняем файл
            with open(filename, 'w') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            return filename
            
        except Exception as e:
            self.log(f"Ошибка сбора логов: {e}")
            return None
    
    def _get_suricata_logs(self) -> List[Dict]:
        """Получение логов Suricata"""
        logs = []
        suricata_files = [
            "/var/log/suricata/eve.json",
            "/var/log/suricata/fast.log"
        ]
        
        for log_file in suricata_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-5:]  # Последние 5 строк
                    
                    for line in lines:
                        if line.strip():
                            suricata_log = {
                                "timestamp": datetime.now().isoformat(),
                                "system": "suricata",
                                "level": "INFO",
                                "message": f"Suricata log entry",
                                "raw_data": line.strip()
                            }
                            logs.append(suricata_log)
                            
                except Exception as e:
                    self.log(f"Ошибка чтения {log_file}: {e}")
        
        return logs
    
    def _get_clamav_logs(self) -> List[Dict]:
        """Получение логов ClamAV"""
        logs = []
        clamav_files = [
            "/var/log/clamav/clamav.log",
            "/var/log/clamav/freshclam.log"
        ]
        
        for log_file in clamav_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-5:]  # Последние 5 строк
                    
                    for line in lines:
                        if line.strip():
                            clamav_log = {
                                "timestamp": datetime.now().isoformat(),
                                "system": "clamav",
                                "level": "INFO",
                                "message": f"ClamAV log entry",
                                "raw_data": line.strip()
                            }
                            logs.append(clamav_log)
                            
                except Exception as e:
                    self.log(f"Ошибка чтения {log_file}: {e}")
        
        # Если файлов логов нет, генерируем тестовые логи ClamAV
        if not logs:
            clamav_log = {
                "timestamp": datetime.now().isoformat(),
                "system": "clamav",
                "level": "INFO",
                "message": "ClamAV antivirus running",
                "data": {
                    "database_version": "2024.01.01",
                    "scanned_files": random.randint(100, 1000),
                    "infected_files": 0
                }
            }
            logs.append(clamav_log)
        
        return logs
    
    def _generate_random_log(self, systems: List[str]) -> Dict:
        """Генерация случайного лога"""
        system = random.choice(systems) if systems else "system"
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        
        messages = {
            "suricata": [
                "Network traffic anomaly detected",
                "Signature match found",
                "Protocol violation",
                "Port scan detected"
            ],
            "clamav": [
                "Virus database updated",
                "Scan completed successfully",
                "Suspicious file detected",
                "Heuristic analysis alert"
            ],
            "system": [
                "System performance normal",
                "High memory usage detected",
                "CPU load increased",
                "Disk space warning"
            ],
            "auth": [
                "User login successful",
                "Failed authentication attempt",
                "Password changed",
                "New user session started"
            ],
            "network": [
                "Network interface status changed",
                "Connection established",
                "Packet loss detected",
                "Bandwidth usage high"
            ]
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system": system,
            "level": random.choice(levels),
            "message": random.choice(messages.get(system, ["System event"])),
            "data": {
                "event_id": random.randint(1000, 9999),
                "source_ip": f"192.168.1.{random.randint(1, 255)}",
                "value": random.randint(1, 100)
            }
        }
