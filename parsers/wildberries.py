import requests
import json
import time
import os
import re
from datetime import datetime
from typing import List, Dict, Any

class WildberriesParser:
    """
    Парсер для Wildberries
    Собирает товары со скидками из разных категорий
    """
    
    def __init__(self):
        self.store_name = 'Wildberries'
        self.base_url = 'https://www.wildberries.ru'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.products = []
        
    def get_categories(self) -> List[Dict[str, str]]:
        """
        Возвращает список категорий для парсинга
        Каждая категория содержит название и URL
        """
        return [
            {'name': 'electronics', 'url': f'{self.base_url}/catalog/elektronika', 'emoji': '📱'},
            {'name': 'phones', 'url': f'{self.base_url}/catalog/mobilnye-telefony', 'emoji': '📱'},
            {'name': 'notebooks', 'url': f'{self.base_url}/catalog/noutbuki', 'emoji': '💻'},
            {'name': 'audio', 'url': f'{self.base_url}/catalog/audio-i-video', 'emoji': '🎧'},
            {'name': 'clothes_men', 'url': f'{self.base_url}/catalog/muzhchinam', 'emoji': '👔'},
            {'name': 'clothes_women', 'url': f'{self.base_url}/catalog/zhenshchinam', 'emoji': '👗'},
            {'name': 'shoes', 'url': f'{self.base_url}/catalog/obuv', 'emoji': '👟'},
            {'name': 'home', 'url': f'{self.base_url}/catalog/tovary-dlya-doma', 'emoji': '🏠'},
            {'name': 'kitchen', 'url': f'{self.base_url}/catalog/kuhnya', 'emoji': '🍳'},
            {'name': 'sport', 'url': f'{self.base_url}/catalog/sport', 'emoji': '⚽'},
            {'name': 'beauty', 'url': f'{self.base_url}/catalog/krasota', 'emoji': '💄'},
            {'name': 'kids', 'url': f'{self.base_url}/catalog/detyam', 'emoji': '🧸'},
            {'name': 'auto', 'url': f'{self.base_url}/catalog/avtotovary', 'emoji': '🚗'},
            {'name': 'garden', 'url': f'{self.base_url}/catalog/dacha-sad-i-ogorod', 'emoji': '🌱'},
            {'name': 'books', 'url': f'{self.base_url}/catalog/knigi', 'emoji': '📚'},
        ]
    
    def fetch_page(self, url: str, retries: int = 3) -> str:
        """
        Загружает HTML страницы с повторными попытками
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 429:
                    # Слишком много запросов
                    wait_time = 10 * (attempt + 1)
                    print(f"⚠️ 429 ошибка. Ждем {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    print(f"⚠️ Статус {response.status_code}. Попытка {attempt + 1}/{retries}")
                    time.sleep(5)
                    
            except requests.exceptions.Timeout:
                print(f"⏰ Таймаут. Попытка {attempt + 1}/{retries}")
                time.sleep(5)
            except requests.exceptions.ConnectionError:
                print(f"🔌 Ошибка соединения. Попытка {attempt + 1}/{retries}")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Неизвестная ошибка: {e}")
                time.sleep(5)
        
        return None
    
    def extract_product_id(self, html: str) -> List[str]:
        """
        Извлекает ID товаров из HTML
        """
        # Ищем ID товаров в разных форматах
        patterns = [
            r'data-nm="(\d+)"',
            r'data-id="(\d+)"',
            r'data-popup-nm="(\d+)"',
            r'/catalog/(\d+)/detail\.aspx',
        ]
        
        ids = []
        for pattern in patterns:
            found = re.findall(pattern, html)
            ids.extend(found)
        
        # Убираем дубликаты
        return list(set(ids))
    
    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        """
        Получает информацию о товаре по ID
        """
        try:
            # Пробуем получить данные через API Wildberries
            api_url = f'https://card.wb.ru/cards/detail?nm={product_id}'
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('products'):
                    product = data['data']['products'][0]
                    
                    # Базовая цена
                    price = product.get('salePriceU', 0) // 100  # В копейках
                    old_price = product.get('priceU', 0) // 100
                    
                    # Скидка
                    if old_price > 0:
                        discount = int(((old_price - price) / old_price) * 100)
                    else:
                        discount = 0
                    
                    return {
                        'id': product_id,
                        'name': product.get('name', ''),
                        'brand': product.get('brand', ''),
                        'price': price,
                        'old_price': old_price,
                        'discount': discount,
                        'rating': product.get('rating', 0),
                        'reviews': product.get('feedbacks', 0),
                        'url': f'https://www.wildberries.ru/catalog/{product_id}/detail.aspx',
                        'image': f'https://images.wbstatic.net/c516x688/{product_id}-1.jpg',
                    }
            
            time.sleep(1)  # Не долбим API слишком часто
            return None
            
        except Exception as e:
            print(f"Ошибка получения товара {product_id}: {e}")
            return None
    
    def calculate_value_score(self, product: Dict[str, Any]) -> int:
        """
        Рассчитывает выгодность товара (0-100)
        """
        score = 0
        reasons = []
        
        # 1. Скидка (максимум 40 баллов)
        discount = product.get('discount', 0)
        if discount >= 70:
            score += 40
            reasons.append("мегаскидка 70%+")
        elif discount >= 50:
            score += 30
            reasons.append("огромная скидка 50%+")
        elif discount >= 30:
            score += 20
            reasons.append("хорошая скидка 30%+")
        elif discount >= 20:
            score += 10
            reasons.append("скидка 20%+")
        
        # 2. Рейтинг (максимум 20 баллов)
        rating = product.get('rating', 0)
        if rating >= 4.8:
            score += 20
            reasons.append("топ-рейтинг 4.8+")
        elif rating >= 4.5:
            score += 15
            reasons.append("высокий рейтинг 4.5+")
        elif rating >= 4.0:
            score += 10
            reasons.append("хороший рейтинг")
        
        # 3. Количество отзывов (максимум 20 баллов)
        reviews = product.get('reviews', 0)
        if reviews >= 1000:
            score += 20
            reasons.append("1000+ отзывов")
        elif reviews >= 500:
            score += 15
            reasons.append("500+ отзывов")
        elif reviews >= 100:
            score += 10
            reasons.append("100+ отзывов")
        
        # 4. Экономия в рублях (максимум 20 баллов)
        savings = product.get('old_price', 0) - product.get('price', 0)
        if savings >= 10000:
            score += 20
            reasons.append(f"экономия {savings:,}₽".replace(',', ' '))
        elif savings >= 5000:
            score += 15
            reasons.append(f"экономия {savings:,}₽".replace(',', ' '))
        elif savings >= 1000:
            score += 10
            reasons.append(f"экономия {savings:,}₽".replace(',', ' '))
        
        product['value_score'] = score
        product['value_reasons'] = reasons
        
        return score
    
    def parse_category(self, category: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Парсит одну категорию
        """
        print(f"📁 Парсим категорию: {category['name']}")
        
        html = self.fetch_page(category['url'])
        if not html:
            print(f"❌ Не удалось загрузить {category['url']}")
            return []
        
        # Получаем ID товаров
        product_ids = self.extract_product_id(html)
        print(f"🔍 Найдено ID товаров: {len(product_ids)}")
        
        # Берем только первые 20, чтобы не перегружать
        product_ids = product_ids[:20]
        
        category_products = []
        for i, pid in enumerate(product_ids):
            print(f"  ⏳ Загружаем товар {i+1}/{len(product_ids)}", end='\r')
            
            product_info = self.get_product_info(pid)
            if product_info:
                product_info['category'] = category['name']
                product_info['store'] = self.store_name
                product_info['emoji'] = category.get('emoji', '🛍️')
                
                # Рассчитываем выгодность
                self.calculate_value_score(product_info)
                
                # Берем только товары со скидкой >= 20%
                if product_info.get('discount', 0) >= 20:
                    category_products.append(product_info)
            
            time.sleep(0.5)  # Задержка между запросами
        
        print(f"\n✅ В категории {category['name']} найдено {len(category_products)} товаров со скидкой")
        return category_products
    
    def parse_all(self) -> List[Dict[str, Any]]:
        """
        Парсит все категории
        """
        print("=" * 60)
        print(f"🚀 ЗАПУСК ПАРСЕРА {self.store_name}")
        print("=" * 60)
        
        categories = self.get_categories()
        all_products = []
        
        for category in categories:
            products = self.parse_category(category)
            all_products.extend(products)
            
            # Сортируем по выгодности внутри категории
            products.sort(key=lambda x: x.get('value_score', 0), reverse=True)
            
            # Небольшая пауза между категориями
            time.sleep(3)
        
        # Общая сортировка
        all_products.sort(key=lambda x: x.get('value_score', 0), reverse=True)
        
        print("=" * 60)
        print(f"📊 ИТОГО: {len(all_products)} товаров со скидкой")
        print("=" * 60)
        
        return all_products

def main():
    """
    Основная функция запуска
    """
    parser = WildberriesParser()
    products = parser.parse_all()
    
    # Создаем папку data если её нет
    os.makedirs('data', exist_ok=True)
    
    # Сохраняем результаты
    output_file = 'data/wildberries.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Сохранено в {output_file}")
    
    # Выводим топ-5 товаров
    print("\n🏆 ТОП-5 САМЫХ ВЫГОДНЫХ ТОВАРОВ:")
    for i, p in enumerate(products[:5], 1):
        print(f"{i}. {p.get('name', 'Без названия')}")
        print(f"   💰 {p.get('price', 0):,}₽ (было {p.get('old_price', 0):,}₽) | 📉 -{p.get('discount', 0)}%".replace(',', ' '))
        print(f"   ⭐ {p.get('rating', 0)} | 👥 {p.get('reviews', 0)} отзывов")
        print(f"   🔥 Выгодность: {p.get('value_score', 0)}/100")
        print()

if __name__ == '__main__':
    main()
