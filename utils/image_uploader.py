#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для загрузки изображений на imgbb.com
"""

import requests
import os
import sys
import tempfile
from typing import Optional

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import IMGBB_API_KEY
except ImportError:
    IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', '')
    print("⚠️ config.py не найден, использую переменные окружения")

class ImageUploader:
    """
    Класс для загрузки изображений на imgbb
    """
    
    def __init__(self):
        self.api_key = IMGBB_API_KEY
        self.api_url = "https://api.imgbb.com/1/upload"
        
        if not self.api_key:
            print("⚠️ API ключ imgbb не найден")
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """
        Загружает файл на imgbb и возвращает URL
        """
        if not self.api_key:
            print("❌ Нет API ключа")
            return None
        
        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as file:
                response = requests.post(
                    self.api_url,
                    params={'key': self.api_key},
                    files={'image': file},
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                image_url = data['data']['url']
                print(f"✅ Изображение загружено: {image_url}")
                return image_url
            else:
                print(f"❌ Ошибка загрузки: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return None
    
    def upload_from_url(self, image_url: str) -> Optional[str]:
        """
        Загружает изображение по URL на imgbb
        """
        if not self.api_key:
            print("❌ Нет API ключа")
            return None
        
        try:
            # Скачиваем изображение
            print(f"📥 Скачиваем изображение: {image_url}")
            response = requests.get(image_url, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Не удалось скачать изображение: {response.status_code}")
                return None
            
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            # Загружаем на imgbb
            result = self.upload_file(tmp_path)
            
            # Удаляем временный файл
            os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def upload_from_bytes(self, image_bytes: bytes) -> Optional[str]:
        """
        Загружает изображение из байтов на imgbb
        """
        if not self.api_key:
            print("❌ Нет API ключа")
            return None
        
        try:
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name
            
            # Загружаем на imgbb
            result = self.upload_file(tmp_path)
            
            # Удаляем временный файл
            os.unlink(tmp_path)
            
            return result
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

def main():
    """
    Тестовая функция
    """
    uploader = ImageUploader()
    
    # Тест с URL
    test_url = "https://via.placeholder.com/300"
    result = uploader.upload_from_url(test_url)
    
    if result:
        print(f"✅ Готово: {result}")
    else:
        print("❌ Тест не удался")

if __name__ == '__main__':
    main()
