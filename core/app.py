#!/usr/bin/env python3
from .logic import SecuritySystemLogic
from gui.main_window import MainWindow

class SecurityAgentApp:
    """Главный класс приложения, связывающий логику и интерфейс"""
    
    def __init__(self, root):
        self.logic = SecuritySystemLogic()
        self.gui = MainWindow(root, self.logic)
