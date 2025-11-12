#!/usr/bin/env python3
import unittest
import tempfile
import os
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock
import sys
import tkinter as tk

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.logic import SecuritySystemLogic, SudoManager
from core.config import ConfigManager
from services.log_collector import LogCollector

class TestSecuritySystemLogic(unittest.TestCase):
    
    def setUp(self):
        """Настройка тестовой среды"""
        self.logic = SecuritySystemLogic()
        # Используем временный файл для конфигурации
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({}, self.temp_config)
        self.temp_config.close()
        self.logic.config_file = self.temp_config.name
        self.logic.load_config()
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    def test_config_management(self):
        """Тест управления конфигурацией"""
        # Тест загрузки конфигурации
        self.logic.config = {'test_key': 'test_value'}
        self.logic.save_config()
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(self.logic.config_file))
        
        # Тест загрузки конфигурации
        self.logic.load_config()
        self.assertEqual(self.logic.config.get('test_key'), 'test_value')
    
    @patch('subprocess.run')
    def test_system_status_check(self, mock_subprocess):
        """Тест проверки статуса системы"""
        # Мокаем успешный ответ systemctl
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = 'active\n'
        
        status = self.logic.check_system_status('suricata')
        self.assertIn('Активна', status)
    
    @patch('subprocess.run')
    def test_get_system_status_info(self, mock_subprocess):
        """Тест получения информации о статусе систем"""
        # Мокаем ответы systemctl
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = 'active\n'
        
        status_info = self.logic.get_system_status_info()
        self.assertIsInstance(status_info, str)
        self.assertIn('СТАТУС СИСТЕМ', status_info)
    
    @patch('subprocess.run')
    def test_is_system_running(self, mock_subprocess):
        """Тест проверки запущена ли система"""
        # Мокаем успешный ответ
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = 'active\n'
        
        result = self.logic.is_system_running('suricata')
        self.assertTrue(result)
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_install_dependencies_without_execution(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест установки зависимостей без реального выполнения"""
        # Мокаем успешное выполнение
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ''
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        result = self.logic.install_dependencies('suricata')
        self.assertIsInstance(result, str)
        # Проверяем, что методы sudo были вызваны
        mock_setup.assert_called_once()
        mock_cleanup.assert_called_once()
    
    def test_get_sudo_status(self):
        """Тест получения статуса sudo"""
        # Тест когда права не настроены
        self.logic.sudo_configured = False
        status = self.logic.get_sudo_status()
        self.assertIn('Не активен', status)
        
        # Тест когда права настроены
        self.logic.sudo_configured = True
        status = self.logic.get_sudo_status()
        self.assertIn('Активен', status)
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_install_system_without_real_installation(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест установки системы без реальной установки"""
        # Мокаем все вызовы
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stderr = ''
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        # Тестируем установку Suricata - должен вернуть сообщение об ошибке скрипта
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stderr = "Скрипт не найден"
        
        result = self.logic.install_system('suricata')
        self.assertIsInstance(result, str)
        self.assertIn('Ошибка', result)
        
        # Проверяем, что sudo методы были вызваны
        mock_setup.assert_called()
        mock_cleanup.assert_called()
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_start_system_without_real_start(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест запуска системы без реального запуска"""
        # Мокаем все вызовы
        mock_subprocess.return_value.returncode = 0
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        result = self.logic.start_system('suricata')
        self.assertIsInstance(result, str)
        
        # Проверяем, что sudo методы были вызваны
        mock_setup.assert_called_once()
        mock_cleanup.assert_called_once()
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_stop_system_without_real_stop(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест остановки системы без реальной остановки"""
        # Мокаем все вызовы
        mock_subprocess.return_value.returncode = 0
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        result = self.logic.stop_system('suricata')
        self.assertIsInstance(result, str)
        
        # Проверяем, что sudo методы были вызваны
        mock_setup.assert_called_once()
        mock_cleanup.assert_called_once()
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_update_system_without_real_update(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест обновления системы без реального обновления"""
        # Мокаем все вызовы
        mock_subprocess.return_value.returncode = 0
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        # Тестируем обновление Suricata
        result = self.logic.update_system('suricata')
        self.assertIsInstance(result, str)
        
        # Тестируем обновление ClamAV
        result = self.logic.update_system('clamav')
        self.assertIsInstance(result, str)
        
        # Проверяем, что sudo методы были вызваны
        self.assertEqual(mock_setup.call_count, 2)
        self.assertEqual(mock_cleanup.call_count, 2)
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_clamav_scan_without_real_scan(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест сканирования ClamAV без реального сканирования"""
        # Мокаем все вызовы
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Scan completed"
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        result = self.logic.run_clamav_scan("/tmp")
        self.assertIsInstance(result, str)
        
        # Проверяем, что sudo методы были вызваны
        mock_setup.assert_called_once()
        mock_cleanup.assert_called_once()

class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        """Настройка тестовой среды"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump({'test_key': 'test_value'}, self.temp_file)
        self.temp_file.close()
        self.config = ConfigManager(self.temp_file.name)
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_config(self):
        """Тест загрузки конфигурации"""
        self.assertEqual(self.config.get('test_key'), 'test_value')
    
    def test_set_and_save_config(self):
        """Тест установки и сохранения конфигурации"""
        self.config.set('new_key', 'new_value')
        self.assertEqual(self.config.get('new_key'), 'new_value')
        
        # Сохраняем и проверяем, что файл обновился
        self.config.save_config()
        
        # Загружаем заново и проверяем
        new_config = ConfigManager(self.temp_file.name)
        self.assertEqual(new_config.get('new_key'), 'new_value')
    
    def test_get_default(self):
        """Тест получения значения по умолчанию"""
        value = self.config.get('non_existent_key', 'default_value')
        self.assertEqual(value, 'default_value')

class TestLogCollector(unittest.TestCase):
    
    def setUp(self):
        """Настройка тестовой среды"""
        self.log_callback = Mock()
        self.collector = LogCollector(self.log_callback)
        self.test_logs_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Очистка после тестов"""
        import shutil
        if os.path.exists(self.test_logs_dir):
            shutil.rmtree(self.test_logs_dir)
    
    def test_create_test_log_file(self):
        """Тест создания тестового файла логов"""
        log_file = self.collector.create_test_log_file(3)
        
        self.assertIsNotNone(log_file)
        self.assertTrue(os.path.exists(log_file))
        
        # Проверяем содержимое файла
        with open(log_file, 'r') as f:
            logs = json.load(f)
            self.assertEqual(len(logs), 3)
            # Проверяем структуру логов
            for log in logs:
                self.assertIn('timestamp', log)
                self.assertIn('system', log)
                self.assertIn('level', log)
                self.assertIn('message', log)
        
        # Очистка
        os.unlink(log_file)
    
    @patch('subprocess.run')
    def test_get_clamav_logs_with_mock(self, mock_subprocess):
        """Тест сбора логов ClamAV с моком"""
        # Мокаем успешное выполнение команды tail
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = """
/tmp/test.txt: Win.Test.EICAR_HDB-1 FOUND
/tmp/test2.exe: Heuristic.Phishing.Email.SpoofedDomain FOUND
INFO: Database updated successfully
"""
        
        logs = self.collector._get_clamav_logs()
        
        # Проверяем, что логи собраны корректно
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]['system'], 'clamav')
        # Проверяем, что найдены записи с FOUND
        found_logs = [log for log in logs if 'FOUND' in log.get('raw_data', '')]
        self.assertGreater(len(found_logs), 0)
    
    def test_determine_clamav_log_level(self):
        """Тест определения уровня лога ClamAV"""
        # Тест для ошибок
        error_line = "ERROR: Database update failed"
        level = self.collector._determine_clamav_log_level(error_line)
        self.assertEqual(level, "ERROR")
        
        # Тест для предупреждений
        warning_line = "WARNING: Suspicious file detected"
        level = self.collector._determine_clamav_log_level(warning_line)
        self.assertEqual(level, "WARNING")
        
        # Тест для обнаруженных угроз
        found_line = "test.txt: EICAR-Test-File FOUND"
        level = self.collector._determine_clamav_log_level(found_line)
        self.assertEqual(level, "ALERT")
        
        # Тест для информационных сообщений
        info_line = "Scan completed successfully"
        level = self.collector._determine_clamav_log_level(info_line)
        self.assertEqual(level, "INFO")
    
    def test_extract_clamav_message(self):
        """Тест извлечения сообщения из лога ClamAV"""
        # Тест для строк с FOUND
        found_line = "/home/user/file.exe: Trojan.Win32.Malware FOUND"
        message = self.collector._extract_clamav_message(found_line)
        self.assertIn('Обнаружена угроза', message)
        self.assertIn('Trojan.Win32.Malware', message)
        
        # Тест для ошибок
        error_line = "ERROR: Cannot access file /root/test.txt"
        message = self.collector._extract_clamav_message(error_line)
        self.assertIn('ClamAV:', message)
        
        # Тест для обычных строк
        normal_line = "ClamAV update completed"
        message = self.collector._extract_clamav_message(normal_line)
        self.assertIn('ClamAV:', message)
    
    def test_generate_random_log(self):
        """Тест генерации случайного лога"""
        systems = ['suricata', 'clamav']
        log_entry = self.collector._generate_random_log(systems)
        
        self.assertIn('timestamp', log_entry)
        self.assertIn('system', log_entry)
        self.assertIn('level', log_entry)
        self.assertIn('message', log_entry)
        self.assertIn('data', log_entry)
        self.assertIn(log_entry['system'], systems)
    
    @patch('services.log_collector.LogCollector.send_file_improved')
    def test_send_test_file_with_mock(self, mock_send):
        """Тест отправки тестового файла с моком"""
        # Мокаем успешную отправку
        mock_send.return_value = True
        
        success = self.collector.send_test_file("http://localhost:8000/api/test", 2)
        self.assertTrue(success)
        mock_send.assert_called_once()
    
    @patch('requests.post')
    def test_send_file_improved_with_local_save(self, mock_post):
        """Тест улучшенной отправки файла с сохранением локально"""
        # Создаем тестовый файл
        test_file = os.path.join(self.test_logs_dir, "test_logs.json")
        test_data = [{"test": "data", "timestamp": "2024-01-01T00:00:00"}]
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Мокаем неудачную отправку (сервер недоступен)
        mock_post.side_effect = Exception("Connection failed")
        
        # Тестируем отправку - должна завершиться с ошибкой
        success = self.collector.send_file_improved(test_file, "http://invalid-url/test")
        self.assertFalse(success)
        
        # Файл должен остаться на месте (закомментирована очистка в коде)
        self.assertTrue(os.path.exists(test_file))

class TestIntegration(unittest.TestCase):
    """Интеграционные тесты без реальных операций"""
    
    @patch('core.logic.SecuritySystemLogic.setup_sudo_permissions')
    @patch('core.logic.SecuritySystemLogic.cleanup_sudo_permissions')
    @patch('subprocess.run')
    def test_complete_workflow_without_execution(self, mock_subprocess, mock_cleanup, mock_setup):
        """Тест полного workflow без реального выполнения"""
        logic = SecuritySystemLogic()
        
        # Мокаем все вызовы
        mock_subprocess.return_value.returncode = 0
        mock_setup.return_value = "✅ Sudo права настроены"
        mock_cleanup.return_value = "✅ Sudo права очищены"
        
        # Тестируем весь workflow
        results = []
        
        # 1. Проверка статуса
        status = logic.check_system_status('suricata')
        results.append(("Status Check", status))
        
        # 2. Установка зависимостей
        deps_result = logic.install_dependencies('suricata')
        results.append(("Dependencies", deps_result))
        
        # 3. Запуск системы
        start_result = logic.start_system('suricata')
        results.append(("Start System", start_result))
        
        # 4. Остановка системы
        stop_result = logic.stop_system('suricata')
        results.append(("Stop System", stop_result))
        
        # 5. Обновление
        update_result = logic.update_system('suricata')
        results.append(("Update", update_result))
        
        # Проверяем, что все операции вернули строковые результаты
        for operation, result in results:
            self.assertIsInstance(result, str, f"{operation} returned non-string result: {result}")
        
        # Проверяем, что sudo методы вызывались достаточно раз
        self.assertGreaterEqual(mock_setup.call_count, 3)
        self.assertGreaterEqual(mock_cleanup.call_count, 3)

class TestGUIFunctionality(unittest.TestCase):
    """Тесты функциональности GUI"""
    
    def setUp(self):
        """Настройка тестовой среды"""
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем окно
    
    def tearDown(self):
        """Очистка после тестов"""
        self.root.destroy()
    
    @patch('core.logic.SecuritySystemLogic')
    def test_gui_initialization(self, mock_logic):
        """Тест инициализации GUI"""
        from core.app import SecurityAgentApp
        
        # Создаем мок логики
        mock_logic_instance = Mock()
        mock_logic.return_value = mock_logic_instance
        
        # Проверяем, что приложение создается без ошибок
        app = SecurityAgentApp(self.root)
        self.assertIsNotNone(app.logic)
        self.assertIsNotNone(app.gui)

def run_fast_tests():
    """Запуск только быстрых тестов"""
    fast_test_cases = [
        TestSecuritySystemLogic,
        TestConfigManager,
        TestLogCollector,
        TestGUIFunctionality
    ]
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for test_case in fast_test_cases:
        suite.addTests(loader.loadTestsFromTestCase(test_case))
    
    return suite

if __name__ == '__main__':
    print("Запуск быстрых тестов System Security Agent...")
    print("=" * 60)
    
    # Запускаем только быстрые тесты
    fast_suite = run_fast_tests()
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(fast_suite)
    
    # Выводим статистику
    print(f"\n{'='*50}")
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print(f"{'='*50}")
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.failures:
        print(f"\nПРОВАЛЕННЫЕ ТЕСТЫ:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nТЕСТЫ С ОШИБКАМИ:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Возвращаем код выхода
    exit_code = 0 if result.wasSuccessful() else 1
    print(f"\nКод выхода: {exit_code}")
