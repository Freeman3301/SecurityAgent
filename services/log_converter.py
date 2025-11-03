#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import Optional, Callable

class LogConverter:
    """Класс для конвертации логов Suricata в текстовый формат"""
    
    def __init__(self, log_callback: Optional[Callable] = None):
        self.log_callback = log_callback
    
    def log(self, message: str):
        """Логирование сообщений"""
        if self.log_callback:
            self.log_callback(message)
    
    def convert_eve_to_text(self, input_file: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        Преобразует eve.json в читаемый текстовый формат
        
        Args:
            input_file: путь к eve.json
            output_file: путь для сохранения (если None - создается временный файл)
        """
        if not os.path.exists(input_file):
            self.log(f"❌ Файл не найден: {input_file}")
            return None
        
        try:
            # Если выходной файл не указан, создаем временный
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"/tmp/suricata_logs_{timestamp}.txt"
            
            # Чтение входного файла
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            results = []
            
            for line in lines:
                try:
                    # Парсим JSON строку
                    entry = json.loads(line.strip())
                    
                    # Форматируем запись в текстовый вид
                    text_entry = self.format_entry_as_text(entry)
                    if text_entry:
                        results.append(text_entry)
                        
                except json.JSONDecodeError:
                    continue  # Пропускаем некорректные JSON строки
                except Exception as e:
                    self.log(f"Ошибка обработки строки: {e}")
                    continue
            
            # Сохраняем результаты
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(result + '\n\n')  # Двойной перенос между записями
            
            self.log(f"✅ Конвертировано {len(results)} записей в файл: {output_file}")
            return output_file
            
        except Exception as e:
            self.log(f"❌ Ошибка конвертации: {e}")
            return None
    
    def format_entry_as_text(self, entry):
        """Форматирует запись eve.json в читаемый текст"""
        
        # Базовые поля
        timestamp = entry.get('timestamp', '')
        event_type = entry.get('event_type', 'unknown')
        
        # Форматируем timestamp
        try:
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%d/%m/%Y-%H:%M:%S.%f')[:-3]
            else:
                formatted_time = 'unknown time'
        except:
            formatted_time = timestamp
        
        # Обрабатываем разные типы событий
        if event_type == 'alert':
            return self.format_alert_text(entry, formatted_time)
        elif event_type == 'http':
            return self.format_http_text(entry, formatted_time)
        elif event_type == 'dns':
            return self.format_dns_text(entry, formatted_time)
        elif event_type == 'tls':
            return self.format_tls_text(entry, formatted_time)
        elif event_type == 'fileinfo':
            return self.format_fileinfo_text(entry, formatted_time)
        elif event_type == 'flow':
            return self.format_flow_text(entry, formatted_time)
        elif event_type == 'stats':
            return self.format_stats_text(entry, formatted_time)
        else:
            return self.format_generic_text(entry, formatted_time)

    def format_alert_text(self, entry, timestamp):
        """Форматирует алерт"""
        alert = entry.get('alert', {})
        signature = alert.get('signature', 'Unknown alert')
        category = alert.get('category', '')
        severity = alert.get('severity', 3)
        
        src_ip = entry.get('src_ip', 'unknown')
        src_port = entry.get('src_port', '')
        dest_ip = entry.get('dest_ip', 'unknown')
        dest_port = entry.get('dest_port', '')
        proto = entry.get('proto', '').upper()
        
        lines = [
            f"[ALERT {timestamp}]",
            f"Сигнатура: {signature}",
            f"От: {src_ip}:{src_port} -> К: {dest_ip}:{dest_port}",
            f"Протокол: {proto} | Категория: {category} | Важность: {severity}"
        ]
        
        return '\n'.join(lines)

    def format_http_text(self, entry, timestamp):
        """Форматирует HTTP события"""
        http = entry.get('http', {})
        hostname = http.get('hostname', 'unknown host')
        method = http.get('http_method', 'unknown method')
        url = http.get('url', '/')
        status = http.get('status', 'unknown status')
        length = http.get('length', 0)
        
        src_ip = entry.get('src_ip', 'unknown')
        
        lines = [
            f"[HTTP {timestamp}]",
            f"Запрос: {method} {hostname}{url}",
            f"Статус: {status} | Размер: {length} байт",
            f"Источник: {src_ip}"
        ]
        
        return '\n'.join(lines)

    def format_dns_text(self, entry, timestamp):
        """Форматирует DNS события"""
        dns = entry.get('dns', {})
        query = dns.get('rrname', 'unknown query')
        query_type = dns.get('rrtype', 'unknown type')
        rcode = dns.get('rcode', 'UNKNOWN')
        
        src_ip = entry.get('src_ip', 'unknown')
        
        # Преобразуем тип запроса в читаемый вид
        type_map = {
            '1': 'A', '2': 'NS', '5': 'CNAME', '6': 'SOA', 
            '12': 'PTR', '15': 'MX', '16': 'TXT', '28': 'AAAA'
        }
        query_type_str = type_map.get(str(query_type), str(query_type))
        
        lines = [
            f"[DNS {timestamp}]",
            f"Запрос: {query_type_str} для {query}",
            f"Код ответа: {rcode}",
            f"Клиент: {src_ip}"
        ]
        
        return '\n'.join(lines)

    def format_tls_text(self, entry, timestamp):
        """Форматирует TLS события"""
        tls = entry.get('tls', {})
        sni = tls.get('sni', '')
        subject = tls.get('subject', '')
        version = tls.get('version', '')
        
        src_ip = entry.get('src_ip', 'unknown')
        dest_ip = entry.get('dest_ip', 'unknown')
        
        lines = [
            f"[TLS {timestamp}]",
            f"SNI: {sni}",
            f"Сертификат: {subject}",
            f"Клиент: {src_ip} -> Сервер: {dest_ip}"
        ]
        
        if version:
            lines.append(f"Версия TLS: {version}")
        
        return '\n'.join(lines)

    def format_fileinfo_text(self, entry, timestamp):
        """Форматирует информацию о файлах"""
        fileinfo = entry.get('fileinfo', {})
        filename = fileinfo.get('filename', 'unknown')
        size = fileinfo.get('size', 0)
        file_type = fileinfo.get('magic', 'unknown type')
        
        src_ip = entry.get('src_ip', 'unknown')
        dest_ip = entry.get('dest_ip', 'unknown')
        
        lines = [
            f"[FILE {timestamp}]",
            f"Файл: {filename}",
            f"Размер: {size} байт | Тип: {file_type}",
            f"Передача: {src_ip} -> {dest_ip}"
        ]
        
        return '\n'.join(lines)

    def format_flow_text(self, entry, timestamp):
        """Форматирует flow события"""
        flow = entry.get('flow', {})
        
        src_ip = entry.get('src_ip', 'unknown')
        src_port = entry.get('src_port', '')
        dest_ip = entry.get('dest_ip', 'unknown')
        dest_port = entry.get('dest_port', '')
        proto = entry.get('proto', '').upper()
        
        lines = [
            f"[FLOW {timestamp}]",
            f"Поток: {src_ip}:{src_port} -> {dest_ip}:{dest_port}",
            f"Протокол: {proto}"
        ]
        
        # Добавляем информацию о состоянии потока
        if flow:
            state = flow.get('state', '')
            reason = flow.get('reason', '')
            if state:
                lines.append(f"Состояние: {state}")
            if reason:
                lines.append(f"Причина завершения: {reason}")
        
        return '\n'.join(lines)

    def format_stats_text(self, entry, timestamp):
        """Форматирует статистику"""
        stats = entry.get('stats', {})
        
        lines = [f"[STATS {timestamp}]"]
        
        # Основная статистика
        if 'uptime' in stats:
            lines.append(f"Время работы: {stats['uptime']} сек")
        
        # Статистика захвата
        capture = stats.get('capture', {})
        if capture:
            kernel_packets = capture.get('kernel_packets', 0)
            kernel_drops = capture.get('kernel_drops', 0)
            errors = capture.get('errors', 0)
            
            lines.append(f"Пакеты: {kernel_packets:,} | Потери: {kernel_drops} | Ошибки: {errors}")
        
        # Статистика детекта
        detect = stats.get('detect', {})
        if detect:
            alerts = detect.get('alert', 0)
            lines.append(f"Обнаружено алертов: {alerts}")
        
        return '\n'.join(lines)

    def format_generic_text(self, entry, timestamp):
        """Форматирует неизвестные типы событий"""
        event_type = entry.get('event_type', 'unknown')
        
        lines = [f"[{event_type.upper()} {timestamp}]"]
        
        # Добавляем основные поля, которые есть в большинстве событий
        src_ip = entry.get('src_ip')
        dest_ip = entry.get('dest_ip')
        
        if src_ip and dest_ip:
            lines.append(f"От: {src_ip} -> К: {dest_ip}")
        
        # Для неизвестных типов просто показываем тип события
        lines.append(f"Тип события: {event_type}")
        
        return '\n'.join(lines)
