import requests
import json
import time
import os
import re
from datetime import datetime
from typing import List, Dict, Any

class AliExpressParser:
    """
    Парсер для AliExpress
    Собирает товары со скидками
    """
    
    def __init__(self):
        self.store_name = 'AliExpress'
        self.base_url = 'https://aliexpress.ru'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.products = []
    
    def get_categories(self) -> List[Dict[str, str]]:
        """
        Возвращает список категорий для парсинга
        """
        return [
            {'name': 'electronics', 'url': f'{self.base_url}/category/electronics', 'emoji': '📱'},
            {'name': 'phones', 'url': f'{self.base_url}/category/smartphones', 'emoji': '📱'},
            {'name': 'clothes', 'url': f'{self.base_url}/category/clothing', 'emoji': '👕'},
            {'name': 'home', 'url': f'{self.base_url}/category/home-garden', 'emoji': '🏠'},
            {'name': 'sport', 'url': f'{self.base_url}/category/sports-entertainment', 'emoji': '⚽'},
            {'name': 'beauty', 'url': f'{self.base_url}/category/beauty-health', 'emoji': '💄'},
        ]
    
    def get_test_products(self) -> List[Dict[str, Any]]:
        """
        Возвращает тестовые товары для демонстрации
        (пока не настроен реальный парсинг AliExpress)
        """
        return [
            {
                'name': 'Xiaomi Redmi Note 13 Pro 8/256GB',
                'price': 18990,
                'old_price': 24990,
                'discount': 24,
                'rating': 4.7,
                'reviews': 3456,
                'url': 'https://aliexpress.ru/item/1234567890.html',
                'image': 'https://ae01.alicdn.com/kf/1234567890.jpg',
                'category': 'electronics',
                'store': self.store_name,
                'emoji': '📱',
                'value_score': 74,
                'value_reasons': ['скидка 24%', 'высокий рейтинг', '3000+ отзывов'],
            },
            {
                'name': 'Умные часы Xiaomi Mi Band 8',
                'price': 2490,
                'old_price': 3490,
                'discount': 29,
                'rating': 4.8,
                'reviews': 7890,
                'url': 'https://aliexpress.ru/item/9876543210.html',
                'image': 'https://ae01.alicdn.com/kf/9876543210.jpg',
                'category': 'electronics',
                'store': self.store_name,
                'emoji': '⌚',
                'value_score': 79,
                'value_reasons': ['скидка 29%', 'топ-рейтинг', '7000+ отзывов'],
            },
            {
                'name': 'Беспроводные наушники Haylou GT5',
                'price': 1590,
                'old_price': 2490,
                'discount': 36,
                'rating': 4.6,
                'reviews': 12345,
                'url': 'https://aliexpress.ru/item/5556667778.html',
                'image': 'https://ae01.alicdn.com/kf/5556667778.jpg',
                'category': 'electronics',
                'store': self.store_name,
                'emoji': '🎧',
                'value_score': 85,
                'value_reasons': ['скидка 36%', '10000+ отзывов', 'экономия 900₽'],
            },
            {
                'name': 'Робот-пылесос Xiaomi Mi Robot Vacuum',
                'price': 12990,
                'old_price': 18990,
                'discount': 32,
                'rating': 4.9,
                'reviews': 2345,
                'url': 'https://aliexpress.ru/item/1112223334.html',
                'image': 'https://ae01.alicdn.com/kf/1112223334.jpg',
                'category': 'home',
                'store': self.store_name,
                'emoji': '🤖',
                'value_score': 88,
                'value_reasons': ['скидка 32%', 'топ-рейтинг 4.9', 'экономия 6,000₽'],
            },
            {
                'name': 'Спортивная куртка мужская',
                'price': 3290,
                'old_price': 4990,
                'discount': 34,
                'rating': 4.5,
                'reviews': 567,
                'url': 'https://aliexpress.ru/item/4445556667.html',
                'image': 'https://ae01.alicdn.com/kf/4445556667.jpg',
                'category': 'clothes',
                'store': self.store_name,
                'emoji': '🧥',
                'value_score': 70,
                'value_reasons': ['скидка 34%', 'экономия 1,700₽'],
            }
        ]
    
    def parse_all(self) -> List[Dict[str, Any]]:
        """
        Парсит все категории
        """
        print("=" * 60)
        print(f"🚀 ЗАПУСК ПАРСЕРА {self.store_name}")
        print("=" * 60)
        
        # Пока используем тестовые данные
        # В следующей версии добавим реальный парсинг
        products = self.get_test_products()
        
        print(f"📊 ИТОГО: {len(products)} товаров со скидкой")
        print("=" * 60)
        
        return products

def main():
    """
    Основная функция запуска
    """
    parser = AliExpressParser()
    products = parser.parse_all()
    
    # Создаем папку data если её нет
    os.makedirs('data', exist_ok=True)
    
    # Сохраняем результаты
    output_file = 'data/aliexpress.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Сохранено в {output_file}")

if __name__ == '__main__':
    main()
