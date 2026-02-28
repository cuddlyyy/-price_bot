import requests
import json
import time
import os
import re
from datetime import datetime
from typing import List, Dict, Any

class OzonParser:
    """
    Парсер для Ozon
    Собирает товары со скидками
    """
    
    def __init__(self):
        self.store_name = 'Ozon'
        self.base_url = 'https://www.ozon.ru'
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
            {'name': 'electronics', 'url': f'{self.base_url}/category/elektronika-15500/', 'emoji': '📱'},
            {'name': 'phones', 'url': f'{self.base_url}/category/smartfony-15501/', 'emoji': '📱'},
            {'name': 'notebooks', 'url': f'{self.base_url}/category/noutbuki-15600/', 'emoji': '💻'},
            {'name': 'clothes', 'url': f'{self.base_url}/category/odezhda-7500/', 'emoji': '👕'},
            {'name': 'shoes', 'url': f'{self.base_url}/category/obuv-7501/', 'emoji': '👟'},
            {'name': 'home', 'url': f'{self.base_url}/category/tovary-dlya-doma-14500/', 'emoji': '🏠'},
            {'name': 'sport', 'url': f'{self.base_url}/category/sport-i-otdyh-12500/', 'emoji': '⚽'},
            {'name': 'beauty', 'url': f'{self.base_url}/category/krasota-i-zdorove-12000/', 'emoji': '💄'},
            {'name': 'kids', 'url': f'{self.base_url}/category/detskie-tovary-8000/', 'emoji': '🧸'},
        ]
    
    def get_test_products(self) -> List[Dict[str, Any]]:
        """
        Возвращает тестовые товары для демонстрации
        (пока не настроен реальный парсинг Ozon)
        """
        return [
            {
                'name': 'Ноутбук Lenovo IdeaPad 3 15.6"',
                'price': 43990,
                'old_price': 54990,
                'discount': 20,
                'rating': 4.6,
                'reviews': 892,
                'url': 'https://www.ozon.ru/product/lenovo-ideapad-3-123456789/',
                'image': 'https://cdn1.ozone.ru/s3/multimedia-w/c1200/1234567890.jpg',
                'category': 'electronics',
                'store': self.store_name,
                'emoji': '💻',
                'value_score': 75,
                'value_reasons': ['хорошая скидка 20%', 'высокий рейтинг', '892 отзыва'],
            },
            {
                'name': 'Кроссовки Nike Air Max',
                'price': 8990,
                'old_price': 12990,
                'discount': 31,
                'rating': 4.7,
                'reviews': 2341,
                'url': 'https://www.ozon.ru/product/nike-air-max-987654321/',
                'image': 'https://cdn1.ozone.ru/s3/multimedia-w/c1200/0987654321.jpg',
                'category': 'sport',
                'store': self.store_name,
                'emoji': '👟',
                'value_score': 88,
                'value_reasons': ['хорошая скидка 31%', 'высокий рейтинг', '2000+ отзывов', 'экономия 4,000₽'],
            },
            {
                'name': 'Пылесос Dyson V8 Absolute',
                'price': 29990,
                'old_price': 39990,
                'discount': 25,
                'rating': 4.9,
                'reviews': 567,
                'url': 'https://www.ozon.ru/product/dyson-v8-absolute-1122334455/',
                'image': 'https://cdn1.ozone.ru/s3/multimedia-w/c1200/1122334455.jpg',
                'category': 'home',
                'store': self.store_name,
                'emoji': '🏠',
                'value_score': 82,
                'value_reasons': ['хорошая скидка 25%', 'топ-рейтинг 4.9', 'экономия 10,000₽'],
            },
            {
                'name': 'Смартфон Samsung Galaxy A54',
                'price': 24990,
                'old_price': 34990,
                'discount': 29,
                'rating': 4.7,
                'reviews': 1234,
                'url': 'https://www.ozon.ru/product/samsung-galaxy-a54-5544332211/',
                'image': 'https://cdn1.ozone.ru/s3/multimedia-w/c1200/5544332211.jpg',
                'category': 'electronics',
                'store': self.store_name,
                'emoji': '📱',
                'value_score': 86,
                'value_reasons': ['хорошая скидка 29%', '1000+ отзывов', 'экономия 10,000₽'],
            },
            {
                'name': 'Кофемашина Philips EP1220',
                'price': 19990,
                'old_price': 29990,
                'discount': 33,
                'rating': 4.8,
                'reviews': 345,
                'url': 'https://www.ozon.ru/product/philips-ep1220-9988776655/',
                'image': 'https://cdn1.ozone.ru/s3/multimedia-w/c1200/9988776655.jpg',
                'category': 'home',
                'store': self.store_name,
                'emoji': '☕',
                'value_score': 84,
                'value_reasons': ['скидка 33%', 'высокий рейтинг', 'экономия 10,000₽'],
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
    parser = OzonParser()
    products = parser.parse_all()
    
    # Создаем папку data если её нет
    os.makedirs('data', exist_ok=True)
    
    # Сохраняем результаты
    output_file = 'data/ozon.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Сохранено в {output_file}")

if __name__ == '__main__':
    main()
