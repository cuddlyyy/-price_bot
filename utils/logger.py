#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для логирования
"""

import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """
    Класс для логирования событий
    """
    
    def __init__(self, name: str = 'price_bot', log_dir: str = 'logs'):
        self.name = name
        self.log_dir = log_dir
        
        # Создаём папку для логов
        os.makedirs(log_dir, exist_ok=True)
        
        # Настраиваем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Формат логов
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Лог в файл (по дням)
        log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Лог в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Информационное сообщение"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Предупреждение"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Ошибка"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Отладочное сообщение"""
        self.logger.debug(message)
    
    def critical(self, message: str):
        """Критическая ошибка"""
        self.logger.critical(message)

# Создаём глобальный экземпляр логгера
logger = Logger()

def get_logger(name: Optional[str] = None) -> Logger:
    """
    Возвращает логгер
    """
    if name:
        return Logger(name)
    return logger

def log_error(error: Exception, context: str = ''):
    """
    Логирует ошибку с контекстом
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg)

def log_info(message: str):
    """
    Логирует информационное сообщение
    """
    logger.info(message)

def log_warning(message: str):
    """
    Логирует предупреждение
    """
    logger.warning(message)
