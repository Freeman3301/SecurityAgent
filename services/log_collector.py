#!/usr/bin/env python3
import json
import os
import random
import psutil
import requests
import subprocess
import socket
from datetime import datetime
from typing import List, Dict, Optional, Callable

class LogCollector:
    """Класс для сбора и генерации логов"""
    
    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
        self.is_sending = False
    
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
            
            # Сбор системных ошибок если выбрано
            if 'system_errors' in selected_systems:
                system_error_logs = self._get_system_error_logs()
                logs.extend(system_error_logs)
            
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
        """Получение логов ClamAV только из указанного файла"""
        logs = []
        clamav_log_file = "/home/freem/CURSACH/CursachV4/scripts_clamav/clamav.log"

        if os.path.exists(clamav_log_file):
            try:
                # Читаем логи через sudo
                result = subprocess.run(
                    ['sudo', 'tail', '-50', clamav_log_file],  # Читаем последние 50 строк
                    capture_output=True,
                    text=True,
                    timeout=10
                )
        
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
            
                    for line in lines:
                        line = line.strip()
                        if line:
                            # ОБНОВЛЕННАЯ ФИЛЬТРАЦИЯ: включаем строки с FOUND
                            if self._is_clamav_important_line(line):
                                log_level = self._determine_clamav_log_level(line)
                        
                                clamav_log = {
                                    "timestamp": datetime.now().isoformat(),
                                    "system": "clamav",
                                    "level": log_level,
                                    "message": self._extract_clamav_message(line),
                                    "raw_data": line,
                                    "log_file": os.path.basename(clamav_log_file),
                                    "file_path": self._extract_file_path(line),
                                    "threat_name": self._extract_threat_name(line)
                                }
                                logs.append(clamav_log)
                else:
                    self.log(f"⚠️ Не удалось прочитать {clamav_log_file} через sudo")
                    self.log(f"   Ошибка: {result.stderr}")
        
            except Exception as e:
                self.log(f"Ошибка чтения {clamav_log_file}: {e}")
        else:
            self.log(f"⚠️ Файл логов ClamAV не найден: {clamav_log_file}")

        # Если нет важных записей, создаем информационное сообщение
        if not logs:
            clamav_log = {
                "timestamp": datetime.now().isoformat(),
                "system": "clamav",
                "level": "INFO",
                "message": "ClamAV: важные события не обнаружены в лог-файле",
                "data": {
                    "log_file": clamav_log_file,
                    "status": "clean",
                    "last_check": datetime.now().isoformat()
                }
            }
            logs.append(clamav_log)

        return logs

    def _is_clamav_important_line(self, line: str) -> bool:
        """Проверяет, содержит ли строка важную информацию ClamAV"""
        line_lower = line.lower()
    
        # Ключевые слова для важных событий ClamAV
        important_keywords = [
            'found',          # Обнаруженные угрозы
            'error',          # Ошибки
            'failed',         # Сбои
            'warning',        # Предупреждения
            'infected',       # Зараженные файлы
            'threat',         # Угрозы
            'virus',          # Вирусы
            'pua',           # Potentially Unwanted Applications
            'heuristic',     # Эвристические обнаружения
            'exploit',       # Эксплойты
            'trojan',        # Трояны
            'malware',       # Вредоносное ПО
            'cve_'           # Уязвимости CVE
        ]
    
        # Проверяем наличие ключевых слов
        for keyword in important_keywords:
            if keyword in line_lower:
                return True
    
        return False

    def _determine_clamav_log_level(self, line: str) -> str:
        """Определяет уровень лога ClamAV на основе содержимого"""
        line_lower = line.lower()
    
        if any(word in line_lower for word in ['error', 'failed', 'cannot']):
            return "ERROR"
        elif any(word in line_lower for word in ['warning', 'caution', 'suspicious']):
            return "WARNING"
        elif 'found' in line_lower:
            return "ALERT"  # Специальный уровень для обнаруженных угроз
        else:
            return "INFO"

    def _extract_clamav_message(self, line: str) -> str:
        """Извлекает понятное сообщение из строки лога ClamAV"""
        if 'FOUND' in line:
            # Для строк с обнаруженными угрозами
            parts = line.split(':')
            if len(parts) >= 2:
                threat_name = parts[-1].replace('FOUND', '').strip()
                file_path = parts[0].strip()
                return f"Обнаружена угроза {threat_name} в файле {os.path.basename(file_path)}"
    
        elif 'ERROR' in line or 'WARNING' in line:
            # Для ошибок и предупреждений
            if ':' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    return f"ClamAV: {parts[-1].strip()}"
    
        return f"ClamAV: {line[:100]}..." if len(line) > 100 else f"ClamAV: {line}"

    def _extract_file_path(self, line: str) -> str:
        """Извлекает путь к файлу из строки лога"""
        if ':' in line:
            return line.split(':')[0].strip()
        return ""

    def _extract_threat_name(self, line: str) -> str:
        """Извлекает название угрозы из строки лога"""
        if 'FOUND' in line and ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                return parts[1].replace('FOUND', '').strip()
        return ""
    
    def _is_error_or_warning_line(self, line: str) -> bool:
        """Проверяет, содержит ли строка ошибку или предупреждение"""
        line_lower = line.lower()
        
        # Ключевые слова для ошибок
        error_keywords = [
            'error', 'failed', 'failure', 'critical', 'alert',
            'cannot', 'unable', 'denied', 'permission denied',
            'corrupted', 'malformed', 'virus', 'infected', 'threat'
        ]
        
        # Ключевые слова для предупреждений
        warning_keywords = [
            'warning', 'caution', 'notice', 'attention',
            'suspicious', 'heuristic', 'possible', 'detected'
        ]
        
        # Проверяем наличие ключевых слов
        for keyword in error_keywords + warning_keywords:
            if keyword in line_lower:
                return True
        
        return False
    
    def _determine_log_level(self, line: str) -> str:
        """Определяет уровень лога на основе содержимого"""
        line_lower = line.lower()
        
        error_keywords = ['error', 'failed', 'critical', 'alert', 'cannot', 'unable', 'denied']
        warning_keywords = ['warning', 'caution', 'notice', 'suspicious', 'heuristic']
        
        for keyword in error_keywords:
            if keyword in line_lower:
                return "ERROR"
        
        for keyword in warning_keywords:
            if keyword in line_lower:
                return "WARNING"
        
        return "INFO"
    
    def _extract_log_message(self, line: str) -> str:
        """Извлекает понятное сообщение из строки лога"""
        # Убираем временные метки и другую служебную информацию
        if ':' in line:
            # Берем часть после последнего двоеточия
            parts = line.split(':')
            if len(parts) > 1:
                message = parts[-1].strip()
                if message:
                    return f"ClamAV: {message}"
        
        return f"ClamAV: {line[:100]}..." if len(line) > 100 else f"ClamAV: {line}"
    
    def _get_system_error_logs(self) -> List[Dict]:
        """Получение системных ошибок через скрипт"""
        logs = []
        
        try:
            # Запускаем скрипт сбора ошибок
            script_path = "./system_errors_collector.sh"
            if os.path.exists(script_path):
                result = subprocess.run(
                    ['bash', script_path],
                    capture_output=True,
                    text=True,
                    cwd=os.path.dirname(script_path) or '.'
                )
                
                if result.returncode == 0:
                    # Читаем созданные файлы
                    error_dir = "./error_collector"
                    if os.path.exists(error_dir):
                        # Файл dmesg ошибок
                        dmesg_files = [f for f in os.listdir(error_dir) if f.startswith('dmesg_errors_')]
                        if dmesg_files:
                            dmesg_file = os.path.join(error_dir, dmesg_files[-1])  # Последний файл
                            with open(dmesg_file, 'r') as f:
                                dmesg_content = f.read().strip()
                                if dmesg_content:
                                    dmesg_log = {
                                        "timestamp": datetime.now().isoformat(),
                                        "system": "system_errors",
                                        "level": "ERROR",
                                        "message": "Системные ошибки ядра (dmesg)",
                                        "raw_data": dmesg_content[:500] + "..." if len(dmesg_content) > 500 else dmesg_content
                                    }
                                    logs.append(dmesg_log)
                        
                        # Файл journal ошибок
                        journal_files = [f for f in os.listdir(error_dir) if f.startswith('journal_errors_')]
                        if journal_files:
                            journal_file = os.path.join(error_dir, journal_files[-1])
                            with open(journal_file, 'r') as f:
                                journal_content = f.read().strip()
                                if journal_content:
                                    journal_log = {
                                        "timestamp": datetime.now().isoformat(),
                                        "system": "system_errors",
                                        "level": "ERROR", 
                                        "message": "Системные ошибки журнала (journalctl)",
                                        "raw_data": journal_content[:500] + "..." if len(journal_content) > 500 else journal_content
                                    }
                                    logs.append(journal_log)
                    
                    # Очищаем временные файлы
                    for file in os.listdir(error_dir):
                        if file.startswith(('dmesg_errors_', 'journal_errors_')):
                            try:
                                os.remove(os.path.join(error_dir, file))
                            except:
                                pass
        
        except Exception as e:
            self.log(f"Ошибка сбора системных ошибок: {e}")
        
        # Если файлов нет, создаем тестовую запись
        if not logs:
            system_error_log = {
                "timestamp": datetime.now().isoformat(),
                "system": "system_errors",
                "level": "INFO",
                "message": "Системные ошибки не обнаружены",
                "data": {
                    "status": "clean",
                    "last_check": datetime.now().isoformat()
                }
            }
            logs.append(system_error_log)
        
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
            "system_errors": [
                "Kernel error detected",
                "Hardware failure reported",
                "System crash dump analysis",
                "Critical service failure"
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

    # === МЕТОДЫ КОНВЕРТАЦИИ ===
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

    # === УЛУЧШЕННЫЕ МЕТОДЫ ОТПРАВКИ ===
    
    def send_file_improved(self, file_path: str, url: str, convert_suricata: bool = True) -> bool:
        """Улучшенная отправка файла с возможностью конвертации"""
        if not os.path.exists(file_path):
            self.log(f"❌ Файл {file_path} не существует")
            return False
        
        try:
            # Если это файл Suricata и нужно конвертировать
            final_file_path = file_path
            if convert_suricata and ('suricata' in file_path.lower() or 'eve.json' in file_path):
                from .log_converter import LogConverter
                converter = LogConverter(self.log_callback)
                self.log("🔄 Конвертация Suricata логов в текстовый формат...")
                converted_file = converter.convert_eve_to_text(file_path)
                if converted_file:
                    final_file_path = converted_file
                    self.log(f"✅ Файл сконвертирован: {converted_file}")
                else:
                    self.log("⚠️ Не удалось конвертировать файл, отправляем оригинал")
        
            # Получаем дополнительные параметры
            client_ip = self._get_client_ip()
            hostname = self._get_hostname()
            source = self._detect_log_source(file_path)
        
            # Отправка файла с дополнительными параметрами
            with open(final_file_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(final_file_path), f, 'text/plain'),
                    'client_ip': (None, client_ip),
                    'hostname': (None, hostname),
                    'source': (None, source)
                }
                headers = {'User-Agent': 'SystemSecurityAgent/1.0'}
            
                response = requests.post(url, files=files, headers=headers, timeout=300)
            
                if response.status_code in [200, 201]:
                    self.log(f"✅ Файл {os.path.basename(final_file_path)} отправлен")
                    self.log(f"   📝 Параметры: client_ip={client_ip}, hostname={hostname}, source={source}")
                
                    # Удаляем временный сконвертированный файл если он создавался
                    if final_file_path != file_path and os.path.exists(final_file_path):
                        os.remove(final_file_path)
                
                    return True
                else:
                    self.log(f"❌ HTTP {response.status_code}: {response.text[:100]}")
                    return False
                    
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Ошибка сети: {e}")
            return self._send_file_curl_fallback(file_path, url)
        except Exception as e:
            self.log(f"❌ Неожиданная ошибка: {e}")
            return False
    
    def _send_file_curl_fallback(self, file_path: str, url: str) -> bool:
        """Fallback метод отправки через curl"""
        try:
            client_ip = self._get_client_ip()
            hostname = self._get_hostname()
            source = self._detect_log_source(file_path)

            command = [
                'curl', '-v', '-X', 'POST', 
                '-F', f'file=@{file_path}',
                '-F', f'client_ip={client_ip}',
                '-F', f'hostname={hostname}',
                '-F', f'source={source}',
                '--connect-timeout', '30', 
                '--max-time', '300', 
                url
            ]

            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("✅ Файл отправлен (через curl)")
                return True
            else:
                self.log(f"❌ Ошибка curl: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Ошибка curl fallback: {e}")
            return False

    def _get_client_ip(self) -> str:
        """Получает IP адрес клиента"""
        try:
            # Пробуем получить внешний IP
            response = requests.get('https://api.ipify.org', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except:
            pass
    
        # Fallback: получаем локальный IP
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "unknown"

    def _get_hostname(self) -> str:
        """Получает имя хоста"""
        try:
            return socket.gethostname()
        except:
            return "unknown"

    def _detect_log_source(self, file_path: str) -> str:
        """Определяет источник лога на основе имени файла"""
        filename = os.path.basename(file_path).lower()

        if 'suricata' in filename or 'eve.json' in filename:
            return 'suricata'
        elif 'clamav' in filename or 'clamav.log' in filename:
            return 'clamav'
        elif 'system_errors' in filename or 'dmesg' in filename or 'journal' in filename:
            return 'system_errors'
        elif 'system' in filename or 'syslog' in filename:
            return 'system'
        elif 'auth' in filename or 'login' in filename:
            return 'auth'
        elif 'network' in filename:
            return 'network'
        else:
            return 'user file'

    # === БАЗОВЫЕ МЕТОДЫ ОТПРАВКИ ===
    def send_file(self, file_path: str, url: str, convert_suricata: bool = True) -> bool:
        """Отправка файла на сервер (базовый метод)"""
        return self.send_file_improved(file_path, url, convert_suricata)
    
    def test_connection(self, url: str) -> bool:
        """Тестирование соединения с сервером"""
        try:
            test_url = url.replace('/api/analyze_file', '')
            response = requests.get(test_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    # === МЕТОДЫ УПРАВЛЕНИЯ ОТПРАВКОЙ ===
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
                log_file = self.collect_real_logs(selected_systems, logs_per_file)
                if log_file:
                    # Используем улучшенный метод отправки
                    success = self.send_file_improved(log_file, endpoint_url)
                    
                    # Очищаем временный файл
                    #try:
                    #    os.remove(log_file)
                    #except:
                    #    pass
                
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
        
        test_file = self.create_test_log_file(logs_per_file)
        if test_file:
            success = self.send_file_improved(test_file, endpoint_url)
            # Удаляем временный файл
            try:
                os.remove(test_file)
            except:
                pass
            return success
        return False
