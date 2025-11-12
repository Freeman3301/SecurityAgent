#!/usr/bin/env python3
import os
import requests
import subprocess
from datetime import datetime
from typing import Optional, Callable

class LogSender:
    """Класс для отправки логов на сервер"""
    
    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
        
    def log(self, message: str):
        """Логирование сообщений"""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
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
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "unknown"

    def _get_hostname(self) -> str:
        """Получает имя хоста"""
        try:
            import socket
            return socket.gethostname()
        except:
            return "unknown"

    def _detect_log_source(self, file_path: str) -> str:
        """Определяет источник лога на основе имени файла"""
        filename = os.path.basename(file_path).lower()
    
        if 'suricata' in filename or 'eve.json' in filename:
            return 'suricata'
        elif 'clamav' in filename or 'antivirus' in filename:
            return 'clamav'
        elif 'auth' in filename or 'login' in filename:
            return 'auth'
        elif 'system' in filename or 'syslog' in filename:
            return 'system'
        elif 'network' in filename:
            return 'network'
        else:
            return 'user file'

    def test_server_connection(self, url: str) -> bool:
        """Тестирование соединения с сервером"""
        try:
            test_url = url.replace('/api/analyze_file', '')
            response = requests.get(test_url, timeout=10)
            return response.status_code == 200
        except:
            return False
