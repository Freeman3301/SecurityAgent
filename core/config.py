#!/usr/bin/env python3
import json
from pathlib import Path

class ConfigManager:
    """Менеджер конфигурации приложения"""
    
    def __init__(self, config_file=None):
        self.config_file = config_file or Path.home() / '.system_agent_config.json'
        self.config = self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_config(self):
        """Сохранение конфигурации"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        """Получить значение конфигурации"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Установить значение конфигурации"""
        self.config[key] = value
