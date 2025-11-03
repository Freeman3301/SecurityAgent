#!/usr/bin/env python3
import subprocess
import os
import json
import time
from pathlib import Path
import psutil

class SecuritySystemLogic:
    def __init__(self):
        # Конфигурация
        self.config_file = Path.home() / '.system_agent_config.json'
        self.load_config()
        
        # Пути к скриптам
        self.scripts_dir = "/home/freem/CURSACH/CurrentCursach/scripts_suricata"
        self.clamav_scripts_dir = "/home/freem/CURSACH/CurrentCursach/scripts_clamav"
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {}
    
    def save_config(self):
        """Сохранение конфигурации"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    # === ОСНОВНЫЕ ФУНКЦИИ УСТАНОВКИ ===
    
    def install_system(self, system):
        """Установка системы"""
        if system == 'suricata':
            return self.run_suricata_full_installation()
        elif system == 'clamav':
            return self.run_clamav_full_installation()
        else:
            return self.run_installation_script(system)
    
    def run_suricata_full_installation(self):
        """Полная установка Suricata через три скрипта"""
        scripts = [
            ('install_dependencies.sh', "Установка зависимостей"),
            ('install_suricata.sh', "Установка Suricata"), 
            ('setting_system_suricata.py', "Настройка Suricata")
        ]
        
        for script_name, description in scripts:
            script_path = os.path.join(self.scripts_dir, script_name)
            
            try:
                if script_name.endswith('.py'):
                    cmd = ['sudo', 'python', script_path, '--no-update']
                else:
                    cmd = ['sudo', 'bash', script_path]
                
                result = subprocess.run(
                    cmd,
                    cwd=self.scripts_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    return f"❌ Ошибка в {description}: {result.stderr}"
                    
                time.sleep(2)
                
            except subprocess.TimeoutExpired:
                return f"❌ Таймаут в {description}"
            except Exception as e:
                return f"❌ Исключение в {description}: {str(e)}"
        
        return "✅ Suricata полностью установлена и настроена"
    
    def run_clamav_full_installation(self):
        """Полная установка ClamAV"""
        scripts = [
            ('clamav_install.sh', "Установка ClamAV"),
            ('clamav_configurate.sh', "Настройка ClamAV"),
            ('clamav_start.sh', "Запуск ClamAV")
        ]
        
        for script_name, description in scripts:
            script_path = os.path.join(self.clamav_scripts_dir, script_name)
            
            try:
                cmd = ['sudo', 'bash', script_path]
                
                result = subprocess.run(
                    cmd,
                    cwd=self.clamav_scripts_dir,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode != 0:
                    return f"❌ Ошибка в {description}: {result.stderr}"
                    
                time.sleep(2)
                
            except subprocess.TimeoutExpired:
                return f"❌ Таймаут в {description}"
            except Exception as e:
                return f"❌ Исключение в {description}: {str(e)}"
        
        return "✅ ClamAV полностью установлен и настроен"
    
    def run_installation_script(self, system):
        """Установка других систем"""
        scripts = {
            'fail2ban': 'sudo pacman -S --noconfirm fail2ban',
            'auditd': 'sudo pacman -S --noconfirm audit',
        }
        
        if system in scripts:
            try:
                result = subprocess.run(
                    scripts[system],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
                if result.returncode == 0:
                    return "✅ Установка завершена успешно"
                else:
                    return f"❌ Ошибка: {result.stderr}"
            except Exception as e:
                return f"❌ Исключение: {str(e)}"
        
        return "❌ Система не найдена"
    
    # === ОТДЕЛЬНЫЕ ФУНКЦИИ ДЛЯ SURICATA И CLAMAV ===
    
    def install_dependencies(self, system):
        """Установка зависимостей для выбранной системы"""
        if system == 'suricata':
            script_path = os.path.join(self.scripts_dir, 'install_dependencies.sh')
            cmd = ['sudo', 'bash', script_path]
            description = "зависимостей Suricata"
        elif system == 'clamav':
            # Для ClamAV зависимости устанавливаются вместе с пакетом
            return "✅ Зависимости ClamAV устанавливаются автоматически"
        else:
            return "❌ Система не поддерживается"
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.scripts_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ Зависимости {system} установлены успешно"
            else:
                return f"❌ Ошибка установки {description}: {result.stderr}"
                
        except Exception as e:
            return f"❌ Исключение: {str(e)}"
    
    def install_security_system(self, system):
        """Установка выбранной системы безопасности"""
        if system == 'suricata':
            script_path = os.path.join(self.scripts_dir, 'install_suricata.sh')
            cmd = ['bash', script_path]
            description = "Suricata"
        elif system == 'clamav':
            script_path = os.path.join(self.clamav_scripts_dir, 'clamav_install.sh')
            cmd = ['sudo', 'bash', script_path]
            description = "ClamAV"
        else:
            return "❌ Система не поддерживается"
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.scripts_dir if system == 'suricata' else self.clamav_scripts_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ {description} установлена успешно"
            else:
                return f"❌ Ошибка установки {description}: {result.stderr}"
                
        except Exception as e:
            return f"❌ Исключение: {str(e)}"
    
    def configure_system(self, system):
        """Настройка выбранной системы"""
        if system == 'suricata':
            script_path = os.path.join(self.scripts_dir, 'setting_system_suricata.py')
            cmd = ['sudo', 'python', script_path, '--no-update']
            description = "Suricata"
        elif system == 'clamav':
            script_path = os.path.join(self.clamav_scripts_dir, 'clamav_configurate.sh')
            cmd = ['sudo', 'bash', script_path]
            description = "ClamAV"
        else:
            return "❌ Система не поддерживается"
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.scripts_dir if system == 'suricata' else self.clamav_scripts_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"✅ {description} настроена успешно"
            else:
                return f"❌ Ошибка настройки {description}: {result.stderr}"
                
        except Exception as e:
            return f"❌ Исключение: {str(e)}"
    
    # === УПРАВЛЕНИЕ СИСТЕМАМИ ===
    
    def is_system_running(self, system):
        """Проверка запущена ли система"""
        try:
            if system == 'suricata':
                # Проверяем через systemctl
                result = subprocess.run(
                    ['systemctl', 'is-active', 'suricata'],
                    capture_output=True,
                    text=True
                )
                
                # Проверяем через ps aux
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                
                systemctl_running = result.returncode == 0
                process_running = 'suricata' in ps_result.stdout and 'grep' not in ps_result.stdout
                
                return systemctl_running or process_running
                
            elif system == 'clamav':
                # Проверяем службы ClamAV
                services = ['clamav-daemon', 'clamav-freshclam']
                for service in services:
                    result = subprocess.run(
                        ['systemctl', 'is-active', service],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return True
                
                # Проверяем процессы
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                clamav_processes = ['clamd', 'freshclam']
                for process in clamav_processes:
                    if process in ps_result.stdout and 'grep' not in ps_result.stdout:
                        return True
                
                return False
            
        except Exception as e:
            print(f"Ошибка проверки {system}: {e}")
            return False

    def start_system(self, system):
        """Запуск системы"""
        if system == 'suricata':
            return self.start_suricata()
        elif system == 'clamav':
            return self.start_clamav()
        else:
            return f"❌ Система {system} не поддерживается"

    def start_suricata(self):
        """Запуск Suricata"""
        if self.is_system_running('suricata'):
            self.stop_suricata()
            time.sleep(3)
        
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'start', 'suricata'],
                capture_output=True,
                text=True
            )
            
            time.sleep(3)
            
            if self.is_system_running('suricata'):
                return "✅ Suricata запущена"
            else:
                return self.start_suricata_direct()
                
        except Exception as e:
            return f"❌ Исключение при запуске Suricata: {e}"

    def start_clamav(self):
        """Запуск ClamAV"""
        try:
            # Запускаем основные службы ClamAV
            services = ['clamav-daemon', 'clamav-freshclam']
            for service in services:
                result = subprocess.run(
                    ['sudo', 'systemctl', 'start', service],
                    capture_output=True,
                    text=True
                )
            
            time.sleep(3)
            
            if self.is_system_running('clamav'):
                return "✅ ClamAV запущен"
            else:
                # Пробуем прямой запуск
                script_path = os.path.join(self.clamav_scripts_dir, 'clamav_start.sh')
                result = subprocess.run(
                    ['sudo', 'bash', script_path],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return "✅ ClamAV запущен напрямую"
                else:
                    return f"❌ Ошибка запуска ClamAV: {result.stderr}"
                    
        except Exception as e:
            return f"❌ Исключение при запуске ClamAV: {e}"

    def start_suricata_direct(self):
        """Прямой запуск Suricata"""
        try:
            interface_result = subprocess.run(
                ['ip', '-o', 'link', 'show'],
                capture_output=True,
                text=True
            )
            
            interface = 'enp0s3'
            for line in interface_result.stdout.split('\n'):
                if 'state UP' in line and 'lo' not in line:
                    iface = line.split(':')[1].strip()
                    interface = iface
                    break
            
            cmd = ['sudo', 'suricata', '-c', '/etc/suricata/suricata.yaml', '-i', interface, '-D']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"✅ Suricata запущена напрямую на интерфейсе {interface}"
            else:
                return f"❌ Ошибка прямого запуска: {result.stderr}"
                
        except Exception as e:
            return f"❌ Исключение при прямом запуске: {e}"
    
    def stop_system(self, system):
        """Остановка системы"""
        if system == 'suricata':
            return self.stop_suricata()
        elif system == 'clamav':
            return self.stop_clamav()
        else:
            return f"❌ Система {system} не поддерживается"
    
    def stop_suricata(self):
        """Остановка Suricata"""
        pids_before = self.get_process_pids('suricata')
        
        try:
            # 1. Останавливаем через systemctl
            result = subprocess.run(
                ['sudo', 'systemctl', 'stop', 'suricata'],
                capture_output=True,
                text=True
            )
            time.sleep(2)
            
            # 2. Убиваем процессы
            subprocess.run(['sudo', 'pkill', '-f', 'suricata'], capture_output=True, text=True)
            time.sleep(1)
            
            # 3. Убиваем процессы через kill -9
            pids_after_pkill = self.get_process_pids('suricata')
            if pids_after_pkill:
                for pid in pids_after_pkill:
                    try:
                        subprocess.run(['sudo', 'kill', '-9', str(pid)], capture_output=True, text=True)
                    except:
                        pass
            
            # 4. Дополнительная очистка
            subprocess.run(['sudo', 'pkill', '-9', '-f', 'suricata'], capture_output=True, text=True)
            
            # 5. Удаляем pid файлы
            pid_files = ["/var/run/suricata.pid", "/run/suricata.pid"]
            for pid_file in pid_files:
                if os.path.exists(pid_file):
                    subprocess.run(['sudo', 'rm', '-f', pid_file])
            
            time.sleep(2)
            pids_final = self.get_process_pids('suricata')
            
            if not pids_final:
                return "✅ Suricata полностью остановлена"
            else:
                return f"⚠️ Остались процессы: {pids_final}"
                
        except Exception as e:
            return f"❌ Ошибка остановки Suricata: {e}"
    
    def stop_clamav(self):
        """Остановка ClamAV"""
        try:
            # Останавливаем службы
            services = ['clamav-daemon', 'clamav-freshclam']
            for service in services:
                subprocess.run(['sudo', 'systemctl', 'stop', service], capture_output=True, text=True)
            
            time.sleep(2)
            
            # Убиваем процессы
            clamav_processes = ['clamd', 'freshclam']
            for process in clamav_processes:
                subprocess.run(['sudo', 'pkill', '-f', process], capture_output=True, text=True)
                subprocess.run(['sudo', 'pkill', '-9', '-f', process], capture_output=True, text=True)
            
            # Убиваем процессы по PID
            for process in clamav_processes:
                pids = self.get_process_pids(process)
                for pid in pids:
                    try:
                        subprocess.run(['sudo', 'kill', '-9', str(pid)], capture_output=True, text=True)
                    except:
                        pass
            
            time.sleep(2)
            pids_final = []
            for process in clamav_processes:
                pids_final.extend(self.get_process_pids(process))
            
            if not pids_final:
                return "✅ ClamAV полностью остановлен"
            else:
                return f"⚠️ Остались процессы: {pids_final}"
                
        except Exception as e:
            return f"❌ Ошибка остановки ClamAV: {e}"
    
    def update_system(self, system):
        """Обновление системы (правила/базы)"""
        if system == 'suricata':
            return self.update_suricata_rules()
        elif system == 'clamav':
            return self.update_clamav_database()
        else:
            return f"❌ Система {system} не поддерживается"
    
    def update_suricata_rules(self):
        """Обновление правил Suricata"""
        try:
            result = subprocess.run(
                ['sudo', 'suricata-update'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return "✅ Правила Suricata обновлены"
            else:
                return f"❌ Ошибка обновления правил: {result.stderr}"
                
        except Exception as e:
            return f"❌ Исключение: {str(e)}"
    
    def update_clamav_database(self):
        """Обновление базы данных ClamAV"""
        try:
            result = subprocess.run(
                ['sudo', 'freshclam'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return "✅ База данных ClamAV обновлена"
            else:
                return f"❌ Ошибка обновления базы: {result.stderr}"
                
        except Exception as e:
            return f"❌ Исключение: {str(e)}"
    
    def get_process_pids(self, process_name):
        """Получить все PID процессов по имени"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                pids = [pid.strip() for pid in result.stdout.split('\n') if pid.strip()]
                return pids
            return []
        except:
            return []
    
    # === МОНИТОРИНГ И СТАТУС ===
    
    def check_system_status(self, system):
        """Проверка статуса конкретной системы"""
        try:
            services = {
                'suricata': 'suricata',
                'clamav': 'clamav-daemon',
                'fail2ban': 'fail2ban',
                'auditd': 'auditd'
            }
            
            if system in services:
                service_name = services[system]
                
                # Проверяем через systemctl
                result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True
                )
                
                # Проверяем через ps aux
                ps_result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                
                if system == 'clamav':
                    process_running = any(proc in ps_result.stdout for proc in ['clamd', 'freshclam']) and 'grep' not in ps_result.stdout
                else:
                    process_running = system in ps_result.stdout and 'grep' not in ps_result.stdout
                
                if result.returncode == 0 or process_running:
                    return "✅ Активна (systemctl или процесс)"
                else:
                    # Проверяем установлена ли система
                    if system == 'clamav':
                        check_cmd = ['which', 'clamscan']
                    else:
                        check_cmd = ['which', system]
                    
                    result = subprocess.run(check_cmd, capture_output=True)
                    if result.returncode == 0:
                        return "⚠️ Установлена, но не запущена"
                    else:
                        return "❌ Не установлена"
                    
            return "⚠️ Не установлена"
            
        except Exception as e:
            return f"❌ Ошибка проверки: {str(e)}"
    
    def get_system_status_info(self):
        """Получить информацию о статусе всех систем"""
        status_info = "=== СТАТУС СИСТЕМ ===\n\n"
        
        systems = ['suricata', 'clamav', 'fail2ban', 'auditd']
        for system in systems:
            status = self.check_system_status(system)
            status_info += f"{system.upper():<15} {status}\n"
        
        status_info += f"\n=== ИНФОРМАЦИЯ О СИСТЕМЕ ===\n"
        status_info += f"Загрузка CPU: {psutil.cpu_percent()}%\n"
        status_info += f"Использование RAM: {psutil.virtual_memory().percent}%\n"
        
        return status_info
    
    def start_service(self, system):
        """Запуск службы системы"""
        if system == 'suricata':
            return self.start_suricata()
        elif system == 'clamav':
            return self.start_clamav()
        elif system == 'fail2ban':
            try:
                subprocess.run(['sudo', 'systemctl', 'start', 'fail2ban'], capture_output=True)
                return f"✅ {system} запущен"
            except Exception as e:
                return f"❌ Ошибка запуска {system}: {e}"
        elif system == 'auditd':
            try:
                subprocess.run(['sudo', 'systemctl', 'start', 'auditd'], capture_output=True)
                return f"✅ {system} запущен"
            except Exception as e:
                return f"❌ Ошибка запуска {system}: {e}"
        else:
            return f"❌ Система {system} не поддерживается"
    
    def stop_service(self, system):
        """Остановка службы системы"""
        if system == 'suricata':
            return self.stop_suricata()
        elif system == 'clamav':
            return self.stop_clamav()
        elif system == 'fail2ban':
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'fail2ban'], capture_output=True)
                return f"✅ {system} остановлен"
            except Exception as e:
                return f"❌ Ошибка остановки {system}: {e}"
        elif system == 'auditd':
            try:
                subprocess.run(['sudo', 'systemctl', 'stop', 'auditd'], capture_output=True)
                return f"✅ {system} остановлен"
            except Exception as e:
                return f"❌ Ошибка остановки {system}: {e}"
        else:
            return f"❌ Система {system} не поддерживается"
