#!/usr/bin/env python3
import subprocess
import os
import sys
import json
import shutil
from pathlib import Path
import argparse
import logging
import re
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SuricataSetup:
    def __init__(self):
        self.suricata_config = "/etc/suricata/suricata.yaml"
        self.rules_dir = "/var/lib/suricata/rules"
        self.default_interface = None
        
    def check_root(self):
        """Проверка прав root"""
        if os.geteuid() != 0:
            logger.error("Требуются права root! Запустите с sudo")
            sys.exit(1)
        logger.info("Проверка прав root: OK")
    
    def detect_network_interfaces(self):
        """Определение сетевых интерфейсов"""
        try:
            result = subprocess.run(['ip', '-o', 'link', 'show'], 
                                  capture_output=True, text=True, check=True)
            interfaces = []
            for line in result.stdout.split('\n'):
                if 'state UP' in line:
                    iface = line.split(':')[1].strip()
                    if iface != 'lo':  # Исключаем loopback
                        interfaces.append(iface)
            
            logger.info(f"Найдены интерфейсы: {interfaces}")
            
            # Выбираем первый не-loopback интерфейс
            if interfaces:
                self.default_interface = interfaces[0]
                logger.info(f"Выбран интерфейс: {self.default_interface}")
                return interfaces
            else:
                logger.warning("Не найдено активных интерфейсов")
                return []
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка определения интерфейсов: {e}")
            return []
    
    def check_suricata_installed(self):
        """Проверка установки Suricata"""
        if not shutil.which("suricata"):
            logger.error("Suricata не установлена!")
            logger.info("Установите: sudo pacman -S suricata")
            return False
        logger.info("Suricata установлена: OK")
        return True
    
    def check_config_exists(self):
        """Проверка существования конфига"""
        if not os.path.exists(self.suricata_config):
            logger.error(f"Конфиг не найден: {self.suricata_config}")
            logger.info("Создайте конфиг: sudo suricata --dump-config > /etc/suricata/suricata.yaml")
            return False
        logger.info("Конфигурационный файл: OK")
        return True
    
    def check_rules_directory(self):
        """Проверка и создание директории правил"""
        rules_path = Path(self.rules_dir)
        
        if not rules_path.exists():
            logger.warning(f"Директория правил не существует: {self.rules_dir}")
            try:
                rules_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Создана директория: {self.rules_dir}")
            except Exception as e:
                logger.error(f"Ошибка создания директории: {e}")
                return False
        
        # Проверяем права доступа
        if not os.access(self.rules_dir, os.R_OK | os.W_OK):
            logger.error(f"Нет прав доступа к: {self.rules_dir}")
            return False
            
        logger.info("Директория правил: OK")
        return True
    
    def update_suricata_rules(self):
        """Обновление правил Suricata"""
        try:
            logger.info("Обновление правил Suricata...")
            result = subprocess.run(['suricata-update', '--no-test'], 
                                  capture_output=True, text=True, check=True)
            logger.info("Правила обновлены успешно")
            
            # Проверяем наличие файлов правил
            rules_files = list(Path(self.rules_dir).glob('*.rules'))
            if not rules_files:
                logger.warning("Файлы правил не найдены, создаем базовые...")
                return self._create_basic_rules()
                
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка обновления правил: {e}")
            logger.info("Пытаемся создать базовые правила...")
            return self._create_basic_rules()
    
    def _create_basic_rules(self):
        """Создание базовых правил"""
        try:
            basic_rules = """# Basic Suricata rules
alert icmp any any -> any any (msg:"ICMP Ping detected"; sid:1000001; rev:1;)
alert tcp any any -> any 22 (msg:"SSH connection attempt"; sid:1000002; rev:1;)
alert tcp any any -> any 80 (msg:"HTTP connection"; sid:1000003; rev:1;)
alert tcp any any -> any 443 (msg:"HTTPS connection"; sid:1000004; rev:1;)
"""
            
            rules_file = os.path.join(self.rules_dir, "suricata.rules")
            with open(rules_file, 'w') as f:
                f.write(basic_rules)
            
            logger.info(f"Созданы базовые правила: {rules_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания правил: {e}")
            return False
    
    def validate_config_syntax(self):
        """Проверка синтаксиса конфига"""
        try:
            logger.info("Проверка синтаксиса конфигурации...")
            result = subprocess.run(['suricata', '-T', '-c', self.suricata_config], 
                                  capture_output=True, text=True, check=True)
            logger.info("Синтаксис конфига: OK")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка в конфиге: {e.stderr}")
            return False
    
    def modify_config_interface(self, interface):
        """Изменение интерфейса в конфиге"""
        try:
            with open(self.suricata_config, 'r') as f:
                content = f.read()
            
            # Ищем и заменяем интерфейс в af-packet секции
            pattern = r'(af-packet:\s*\n\s*-\s*interface:\s*)(\w+)'
            new_content = re.sub(pattern, f'\\1{interface}', content)
            
            if new_content != content:
                with open(self.suricata_config, 'w') as f:
                    f.write(new_content)
                logger.info(f"Интерфейс изменен на: {interface}")
                return True
            else:
                logger.warning("Интерфейс не найден в конфиге, потребуется ручное изменение")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка изменения конфига: {e}")
            return False
    
    def is_suricata_running(self):
        """Проверка, запущена ли Suricata"""
        try:
            result = subprocess.run(['pgrep', 'suricata'], 
                                  capture_output=True, text=True)
            return result.returncode == 0 and result.stdout.strip() != ''
        except:
            return False
    
    def stop_suricata(self):
        """Корректная остановка Suricata"""
        try:
            # Пробуем через systemctl
            result = subprocess.run(['systemctl', 'stop', 'suricata'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Suricata остановлена через systemctl")
                return True
            
            # Если systemctl не сработал, убиваем процесс
            return self.force_stop_suricata()
            
        except Exception as e:
            logger.error(f"Ошибка остановки Suricata: {e}")
            return self.force_stop_suricata()
    
    def force_stop_suricata(self):
        """Принудительная остановка Suricata"""
        try:
            # Ищем и убиваем все процессы suricata
            result = subprocess.run(['pkill', '-9', 'suricata'], 
                                  capture_output=True, text=True)
            
            # Удаляем pid файл
            pid_file = "/var/run/suricata.pid"
            if os.path.exists(pid_file):
                os.remove(pid_file)
                logger.info("Удален старый pid файл")
            
            logger.info("Suricata принудительно остановлена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка принудительной остановки: {e}")
            return False
    
    def start_suricata(self, interface=None):
        """Запуск Suricata с проверкой уже запущенного процесса"""
        if not interface:
            interface = self.default_interface
            
        try:
            logger.info(f"Запуск Suricata на интерфейсе: {interface}")
            
            # Проверяем, не запущена ли уже Suricata
            if self.is_suricata_running():
                logger.warning("Suricata уже запущена, останавливаем...")
                if not self.stop_suricata():
                    logger.error("Не удалось остановить работающую Suricata")
                    return False
                
                # Ждем завершения процесса
                time.sleep(2)
            
            # Проверяем и удаляем старый pid файл
            pid_file = "/var/run/suricata.pid"
            if os.path.exists(pid_file):
                try:
                    os.remove(pid_file)
                    logger.info("Удален старый pid файл")
                except Exception as e:
                    logger.warning(f"Не удалось удалить pid файл: {e}")
            
            # Запускаем Suricata
            cmd = ['suricata', '-c', self.suricata_config, '-i', interface, '-D']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            logger.info("Suricata успешно запущена в фоновом режиме")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка запуска Suricata: {e.stderr}")
            
            # Дополнительная диагностика
            if "pid file" in e.stderr and "exists" in e.stderr:
                logger.info("Пытаемся принудительно остановить Suricata...")
                self.force_stop_suricata()
                # Повторяем попытку запуска
                time.sleep(2)
                return self.start_suricata(interface)
                
            return False

    def check_suricata_running(self):
        """Проверка работы Suricata - простая версия"""
        try:
            # Простая проверка через systemctl
            result = subprocess.run(['systemctl', 'is-active', 'suricata'], 
                              capture_output=True, text=True)
        
            if result.returncode == 0 and 'active' in result.stdout:
                logger.info("Suricata запущена (systemctl)")
                return True
        
            # Или через ps
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            if 'suricata' in result.stdout and 'grep' not in result.stdout:
                logger.info("Suricata запущена (ps aux)")
                return True
            
            logger.error("Suricata не запущена")
            return False
        
        except Exception as e:
            logger.error(f"Ошибка проверки процесса: {e}")
            return False

    def show_logs(self, lines=10):
        """Показать последние логи"""
        log_file = "/var/log/suricata/suricata.log"
        eve_file = "/var/log/suricata/eve.json"
        
        if os.path.exists(log_file):
            logger.info(f"Последние {lines} строк лога:")
            result = subprocess.run(['tail', f'-n{lines}', log_file], 
                                  capture_output=True, text=True)
            print(result.stdout)
        
        if os.path.exists(eve_file):
            logger.info(f"Последние {lines} событий EVE:")
            try:
                result = subprocess.run(['tail', f'-n{lines}', eve_file], 
                                      capture_output=True, text=True)
                print(result.stdout)
            except:
                pass

def main():
    parser = argparse.ArgumentParser(description='Suricata Setup and Launcher')
    parser.add_argument('--interface', '-i', help='Сетевой интерфейс')
    parser.add_argument('--no-update', action='store_true', help='Не обновлять правила')
    parser.add_argument('--check-only', action='store_true', help='Только проверка')
    parser.add_argument('--show-logs', type=int, nargs='?', const=10, 
                       help='Показать логи (количество строк)')
    
    args = parser.parse_args()
    
    setup = SuricataSetup()
    
    # Проверка прав
    setup.check_root()
    
    if args.show_logs:
        setup.show_logs(args.show_logs)
        return
    
    # Определение интерфейсов
    interfaces = setup.detect_network_interfaces()
    if not interfaces:
        logger.error("Не найдено сетевых интерфейсов!")
        return
    
    # Выбор интерфейса
    selected_interface = args.interface if args.interface else setup.default_interface
    if not selected_interface:
        logger.error("Не удалось определить интерфейс!")
        return
    
    logger.info(f"Используется интерфейс: {selected_interface}")
    
    # Проверки
    if not setup.check_suricata_installed():
        return
    
    if not setup.check_config_exists():
        return
    
    if not setup.check_rules_directory():
        return
    
    # Обновление правил
    if not args.no_update:
        if not setup.update_suricata_rules():
            logger.warning("Продолжаем без обновления правил")
    
    # Изменение интерфейса в конфиге
    setup.modify_config_interface(selected_interface)
    
    # Проверка синтаксиса
    if not setup.validate_config_syntax():
        logger.error("Исправьте ошибки в конфиге!")
        return
    
    if args.check_only:
        logger.info("Проверка завершена успешно!")
        return
    
    # Запуск Suricata
    if setup.start_suricata(selected_interface):
        # Проверка запуска
        time.sleep(2)
        if setup.check_suricata_running():
            logger.info("✅ Suricata успешно запущена!")
            logger.info("Для просмотра логов: sudo tail -f /var/log/suricata/eve.json")
        else:
            logger.error("❌ Suricata не запустилась")
    else:
        logger.error("❌ Не удалось запустить Suricata")

if __name__ == "__main__":
    main()
