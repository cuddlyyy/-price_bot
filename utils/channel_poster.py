#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль для автоматического постинга в Telegram канал
Берёт лучшие товары из всех парсеров и публикует их
"""

import requests
import json
import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Добавляем путь к проекту для импорта config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import BOT_TOKEN, CHANNEL_ID
except ImportError:
    # Если config не найден, используем переменные окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    CHANNEL_ID = os.getenv('CHANNEL_ID', '@PriceHunterSK')
    print("⚠️ config.py не найден, использую переменные окружения")

class ChannelPoster:
    """
    Класс для постинга в Telegram канал
    """
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.channel_id = CHANNEL_ID
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.data_dir = 'data'
        
    def load_all_products(self) -> List[Dict[str, Any]]:
        """
        Загружает все товары из всех JSON файлов в папке data
        """
        all_products = []
        
        if not os.path.exists(self.data_dir):
            print(f"❌ Папка {self.data_dir} не найдена")
            return []
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json') and filename != 'users.json':
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        products = json.load(f)
                        if isinstance(products, list):
                            all_products.extend(products)
                            print(f"📦 Загружено {len(products)} товаров из {filename}")
                except Exception as e:
                    print(f"❌ Ошибка загрузки {filename}: {e}")
        
        return all_products
    
    def calculate_final_score(self, product: Dict[str, Any]) -> int:
        """
        Рассчитывает итоговую выгодность товара для сортировки
        """
        score = product.get('value_score', 0)
        
        # Дополнительные бонусы
        discount = product.get('discount', 0)
        if discount > 50:
            score += 20
        elif discount > 40:
            score += 10
        elif discount > 30:
            score += 5
        
        # Бонус за свежесть (чем новее товар, тем лучше)
        # В будущем можно добавить
        
        return score
    
    def get_best_products(self, count: int = 2) -> List[Dict[str, Any]]:
        """
        Выбирает лучшие товары для публикации
        """
        products = self.load_all_products()
        
        if not products:
            print("⚠️ Нет товаров для публикации")
            return []
        
        # Добавляем финальный счёт
        for p in products:
            p['final_score'] = self.calculate_final_score(p)
        
        # Сортируем по убыванию выгодности
        products.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        # Берём лучшие
        best = products[:count]
        print(f"🏆 Выбрано {len(best)} лучших товаров")
        
        return best
    
    def format_price(self, price: Optional[int]) -> str:
        """
        Форматирует цену с пробелами
        """
        if not price:
            return "0"
        return f"{price:,}".replace(',', ' ')
    
    def format_post(self, product: Dict[str, Any]) -> str:
        """
        Форматирует пост для Telegram канала
        """
        # Получаем данные
        name = product.get('name', 'Товар без названия')
        price = product.get('price', product.get('sale_price', 0))
        old_price = product.get('old_price', product.get('regular_price', 0))
        discount = product.get('discount', 0)
        rating = product.get('rating', 0)
        reviews = product.get('reviews', 0)
        store = product.get('store', 'Магазин')
        url = product.get('url', '#')
        emoji = product.get('emoji', '🛍️')
        reasons = product.get('value_reasons', [])
        
        # Форматируем цены
        price_str = self.format_price(price)
        old_price_str = self.format_price(old_price)
        
        # Оценка выгодности для заголовка
        if discount >= 50:
            fire = "🔥🔥🔥 МЕГАСКИДКА"
        elif discount >= 40:
            fire = "🔥🔥 ГОРЯЧЕЕ ПРЕДЛОЖЕНИЕ"
        elif discount >= 30:
            fire = "🔥 ОТЛИЧНАЯ СКИДКА"
        elif discount >= 20:
            fire = "✅ ХОРОШАЯ СКИДКА"
        else:
            fire = "💰 ВЫГОДНО"
        
        # Формируем причины выгодности
        reasons_text = ""
        if reasons:
            reasons_text = "\n".join([f"  • {r}" for r in reasons[:3]])
        
        # Основной текст
        text = f"""🔥 <b>{fire}</b> 🔥

{emoji} <b>{name}</b>

💰 <b>{price_str}₽</b> вместо {old_price_str}₽
📉 СКИДКА: {discount}%

⭐ Рейтинг: {rating} | 👥 {reviews} отзывов
🏪 Магазин: {store}

"""
        
        if reasons_text:
            text += f"✨ <b>Почему выгодно:</b>\n{reasons_text}\n\n"
        
        text += f"""👉 <a href='{url}'>КУПИТЬ СО СКИДКОЙ</a>

⚡️ <b>Хочешь получать такие предложения каждый час?</b>
➡️ @PriceHunter2bot

📢 <b>Наш канал:</b> @PriceHunterSK"""
        
        return text
    
    def send_to_channel(self, text: str, image_url: Optional[str] = None) -> bool:
        """
        Отправляет сообщение в Telegram канал
        """
        if not self.bot_token:
            print("❌ Нет BOT_TOKEN")
            return False
        
        try:
            if image_url:
                # Отправляем с фото
                response = requests.post(
                    f"{self.api_url}/sendPhoto",
                    data={
                        'chat_id': self.channel_id,
                        'photo': image_url,
                        'caption': text,
                        'parse_mode': 'HTML'
                    },
                    timeout=30
                )
            else:
                # Отправляем без фото
                response = requests.post(
                    f"{self.api_url}/sendMessage",
                    data={
                        'chat_id': self.channel_id,
                        'text': text,
                        'parse_mode': 'HTML',
                        'disable_web_page_preview': False
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                print(f"✅ Пост успешно отправлен в {datetime.now()}")
                return True
            else:
                print(f"❌ Ошибка отправки: {response.status_code}")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при отправке: {e}")
            return False
    
    def post_best_deals(self, count: int = 2) -> bool:
        """
        Публикует лучшие товары в канал
        """
        print("=" * 60)
        print(f"🚀 ЗАПУСК ПОСТИНГА В КАНАЛ {datetime.now()}")
        print("=" * 60)
        
        products = self.get_best_products(count)
        
        if not products:
            print("⚠️ Нет товаров для публикации")
            return False
        
        success_count = 0
        for i, product in enumerate(products, 1):
            print(f"\n📝 Пост {i}/{len(products)}: {product.get('name', 'Без названия')[:50]}...")
            
            text = self.format_post(product)
            image_url = product.get('image', product.get('image_url'))
            
            if self.send_to_channel(text, image_url):
                success_count += 1
            
            # Пауза между постами
            if i < len(products):
                print("⏳ Ждём 60 секунд перед следующим постом...")
                time.sleep(60)
        
        print("\n" + "=" * 60)
        print(f"✅ Постинг завершён. Отправлено: {success_count}/{len(products)}")
        print("=" * 60)
        
        return success_count > 0

def main():
    """
    Основная функция для запуска из командной строки
    """
    poster = ChannelPoster()
    poster.post_best_deals(2)

if __name__ == '__main__':
    main()
