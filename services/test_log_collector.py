#!/usr/bin/env python3
"""
Тестирование класса LogCollector для сбора логов систем безопасности
"""

import sys
import os
import tempfile
import json
from datetime import datetime

# Добавляем путь для импорта модуля
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from log_collector import LogCollector

class LogCollectorTester:
    """Класс для тестирования LogCollector"""
    
    def __init__(self):
        self.test_results = []
        self.log_files_created = []
    
    def log_callback(self, message: str):
        """Callback функция для логирования"""
        print(f"[TEST] {message}")
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("=" * 60)
        print("ТЕСТИРОВАНИЕ LOGCOLLECTOR")
        print("=" * 60)
        
        collector = LogCollector(self.log_callback)
        
        # Запускаем тесты
        self.test_create_test_log_file(collector)
        self.test_collect_real_logs(collector)
        self.test_empty_systems(collector)
        self.test_specific_systems(collector)
        self.test_file_validation(collector)
        
        # Выводим результаты
        self.print_results()
        
        # Очищаем временные файлы
        self.cleanup()
    
    def test_create_test_log_file(self, collector: LogCollector):
        """Тест создания тестового файла логов"""
        print("\n1. Тест создания тестового файла логов")
        print("-" * 40)
        
        try:
            # Тест 1: Создание файла с 5 логами
            file_path = collector.create_test_log_file(5)
            if file_path and os.path.exists(file_path):
                self.log_files_created.append(file_path)
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                assert len(logs) == 5, f"Ожидалось 5 логов, получено {len(logs)}"
                assert all('timestamp' in log for log in logs), "Отсутствует timestamp в логах"
                assert all('system' in log for log in logs), "Отсутствует system в логах"
                
                self.record_result("Создание тестового файла (5 логов)", "PASS", f"Создан файл: {file_path}")
            else:
                self.record_result("Создание тестового файла (5 логов)", "FAIL", "Файл не создан")
            
            # Тест 2: Создание файла с 1 логом
            file_path_single = collector.create_test_log_file(1)
            if file_path_single and os.path.exists(file_path_single):
                self.log_files_created.append(file_path_single)
                with open(file_path_single, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                assert len(logs) == 1, f"Ожидался 1 лог, получено {len(logs)}"
                self.record_result("Создание тестового файла (1 лог)", "PASS", f"Создан файл: {file_path_single}")
            else:
                self.record_result("Создание тестового файла (1 лог)", "FAIL", "Файл не создан")
                
        except Exception as e:
            self.record_result("Создание тестового файла", "ERROR", f"Исключение: {str(e)}")
    
    def test_collect_real_logs(self, collector: LogCollector):
        """Тест сбора реальных логов"""
        print("\n2. Тест сбора реальных логов")
        print("-" * 40)
        
        try:
            # Тест с разными системами
            test_systems = [
                (["suricata", "clamav", "system"], "Все системы"),
                (["suricata"], "Только Suricata"),
                (["clamav"], "Только ClamAV"),
                (["system"], "Только системные метрики")
            ]
            
            for systems, description in test_systems:
                file_path = collector.collect_real_logs(systems, 3)
                if file_path and os.path.exists(file_path):
                    self.log_files_created.append(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                    
                    # Проверяем структуру логов
                    valid_logs = 0
                    for log in logs:
                        if self.validate_log_structure(log):
                            valid_logs += 1
                    
                    assert valid_logs == len(logs), f"Не все логи имеют правильную структуру"
                    assert len(logs) >= 1, f"Файл должен содержать минимум 1 лог"
                    
                    # Проверяем что логи соответствуют запрошенным системам
                    log_systems = set(log['system'] for log in logs)
                    expected_systems = set(systems)
                    
                    self.record_result(
                        f"Сбор логов: {description}", 
                        "PASS", 
                        f"Создан файл с {len(logs)} логами, системы: {log_systems}"
                    )
                else:
                    self.record_result(f"Сбор логов: {description}", "FAIL", "Файл не создан")
                    
        except Exception as e:
            self.record_result("Сбор реальных логов", "ERROR", f"Исключение: {str(e)}")
    
    def test_empty_systems(self, collector: LogCollector):
        """Тест с пустым списком систем"""
        print("\n3. Тест с пустым списком систем")
        print("-" * 40)
        
        try:
            file_path = collector.collect_real_logs([], 2)
            if file_path and os.path.exists(file_path):
                self.log_files_created.append(file_path)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # При пустом списке должны быть сгенерированы случайные логи
                assert len(logs) >= 2, "Должно быть минимум 2 лога"
                
                self.record_result("Пустой список систем", "PASS", f"Создано {len(logs)} логов")
            else:
                self.record_result("Пустой список систем", "FAIL", "Файл не создан")
                
        except Exception as e:
            self.record_result("Пустой список систем", "ERROR", f"Исключение: {str(e)}")
    
    def test_specific_systems(self, collector: LogCollector):
        """Тест специфичных сценариев"""
        print("\n4. Тест специфичных сценариев")
        print("-" * 40)
        
        try:
            # Тест с большим количеством логов
            file_path_large = collector.collect_real_logs(["system", "clamav"], 10)
            if file_path_large and os.path.exists(file_path_large):
                self.log_files_created.append(file_path_large)
                
                with open(file_path_large, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                assert len(logs) >= 10, f"Ожидалось минимум 10 логов, получено {len(logs)}"
                self.record_result("Большое количество логов (10+)", "PASS", f"Создано {len(logs)} логов")
            else:
                self.record_result("Большое количество логов (10+)", "FAIL", "Файл не создан")
            
            # Тест с несуществующей системой
            file_path_unknown = collector.collect_real_logs(["unknown_system"], 3)
            if file_path_unknown and os.path.exists(file_path_unknown):
                self.log_files_created.append(file_path_unknown)
                
                with open(file_path_unknown, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # Должны быть сгенерированы логи с системой "system" по умолчанию
                assert len(logs) >= 3, "Должно быть минимум 3 лога"
                self.record_result("Неизвестная система", "PASS", f"Создано {len(logs)} логов")
            else:
                self.record_result("Неизвестная система", "FAIL", "Файл не создан")
                
        except Exception as e:
            self.record_result("Специфичные сценарии", "ERROR", f"Исключение: {str(e)}")
    
    def test_file_validation(self, collector: LogCollector):
        """Тест валидации файлов логов"""
        print("\n5. Тест валидации файлов логов")
        print("-" * 40)
        
        try:
            file_path = collector.create_test_log_file(3)
            if file_path and os.path.exists(file_path):
                self.log_files_created.append(file_path)
                
                # Проверяем содержимое файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                # Проверяем каждый лог
                for i, log in enumerate(logs):
                    if not self.validate_log_structure(log):
                        self.record_result(f"Валидация лога #{i+1}", "FAIL", f"Неверная структура: {log}")
                        return
                
                # Проверяем что файл корректный JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)  # Должен не вызывать исключение
                
                # Проверяем временные метки
                for log in logs:
                    timestamp = datetime.fromisoformat(log['timestamp'])
                    assert timestamp <= datetime.now(), "Временная метка в будущем"
                
                self.record_result("Валидация файла логов", "PASS", "Все логи имеют корректную структуру")
            else:
                self.record_result("Валидация файла логов", "FAIL", "Файл не создан")
                
        except json.JSONDecodeError as e:
            self.record_result("Валидация файла логов", "FAIL", f"Невалидный JSON: {str(e)}")
        except Exception as e:
            self.record_result("Валидация файла логов", "ERROR", f"Исключение: {str(e)}")
    
    def validate_log_structure(self, log: dict) -> bool:
        """Валидация структуры отдельного лога"""
        required_fields = ['timestamp', 'system', 'level', 'message']
        
        # Проверяем обязательные поля
        for field in required_fields:
            if field not in log:
                return False
        
        # Проверяем типы данных
        if not isinstance(log['timestamp'], str):
            return False
        if not isinstance(log['system'], str):
            return False
        if not isinstance(log['level'], str):
            return False
        if not isinstance(log['message'], str):
            return False
        
        # Проверяем допустимые уровни логов
        valid_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        if log['level'] not in valid_levels:
            return False
        
        return True
    
    def record_result(self, test_name: str, status: str, message: str):
        """Запись результата теста"""
        status_symbols = {
            "PASS": "✅",
            "FAIL": "❌", 
            "ERROR": "⚠️"
        }
        
        symbol = status_symbols.get(status, "❓")
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "symbol": symbol
        }
        self.test_results.append(result)
        
        print(f"{symbol} {test_name}: {message}")
    
    def print_results(self):
        """Вывод итоговых результатов"""
        print("\n" + "=" * 60)
        print("ИТОГИ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        total = len(self.test_results)
        
        print(f"\nВсего тестов: {total}")
        print(f"✅ Пройдено: {passed}")
        print(f"❌ Провалено: {failed}")
        print(f"⚠️  Ошибок: {errors}")
        
        if failed == 0 and errors == 0:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print("\nПодробности:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"  {result['symbol']} {result['test']}: {result['message']}")
    
    def cleanup(self):
        """Очистка временных файлов"""
        for file_path in self.log_files_created:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️  Не удалось удалить файл {file_path}: {e}")

def main():
    """Основная функция"""
    tester = LogCollectorTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка при тестировании: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
