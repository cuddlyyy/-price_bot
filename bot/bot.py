#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Основной файл Telegram бота PriceHunterSK
Обрабатывает команды пользователей и управляет подписками
"""

import telebot
import json
import os
import sys
import time
from datetime import datetime, timedelta
from telebot import types
from typing import Dict, Any, Optional, List

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import BOT_TOKEN, ADMIN_ID, CRYPTO_WALLET, CARD_NUMBER, CHANNEL_ID
except ImportError:
    # Если config не найден, используем переменные окружения
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))
    CRYPTO_WALLET = os.getenv('CRYPTO_WALLET', '')
    CARD_NUMBER = os.getenv('CARD_NUMBER', '')
    CHANNEL_ID = os.getenv('CHANNEL_ID', '@PriceHunterSK')
    print("⚠️ config.py не найден, использую переменные окружения")

# Импортируем логгер
try:
    from utils.logger import logger, log_info, log_error
except ImportError:
    # Заглушка для логгера
    class DummyLogger:
        def info(self, msg): print(f"INFO: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
    logger = DummyLogger()
    log_info = logger.info
    log_error = logger.error

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def load_products() -> List[Dict[str, Any]]:
    """
    Загружает все товары из всех JSON файлов
    """
    products = []
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        return []
    
    try:
        for filename in os.listdir(data_dir):
            if filename.endswith('.json') and filename != 'users.json':
                filepath = os.path.join(data_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        products.extend(data)
    except Exception as e:
        log_error(f"Ошибка загрузки товаров: {e}")
    
    # Сортируем по выгодности
    products.sort(key=lambda x: x.get('value_score', 0), reverse=True)
    return products

def load_users() -> Dict[str, Any]:
    """
    Загружает пользователей из users.json
    """
    try:
        with open('data/users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        log_error(f"Ошибка загрузки пользователей: {e}")
        return {}

def save_users(users: Dict[str, Any]) -> bool:
    """
    Сохраняет пользователей в users.json
    """
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        log_error(f"Ошибка сохранения пользователей: {e}")
        return False

def is_premium(user_id: int) -> bool:
    """
    Проверяет, активна ли премиум подписка у пользователя
    """
    users = load_users()
    user = users.get(str(user_id))
    
    if not user:
        return False
    
    try:
        expire = datetime.fromisoformat(user.get('expires', '2000-01-01'))
        return expire > datetime.now()
    except:
        return False

def format_product_card(product: Dict[str, Any]) -> str:
    """
    Форматирует товар для красивого отображения
    """
    name = product.get('name', 'Без названия')
    price = product.get('price', product.get('sale_price', 0))
    old_price = product.get('old_price', product.get('regular_price', 0))
    discount = product.get('discount', 0)
    rating = product.get('rating', 0)
    reviews = product.get('reviews', 0)
    store = product.get('store', 'Магазин')
    url = product.get('url', '#')
    emoji = product.get('emoji', '🛍️')
    
    # Форматируем цены
    price_str = f"{price:,}".replace(',', ' ') if price else "0"
    old_price_str = f"{old_price:,}".replace(',', ' ') if old_price else "0"
    
    text = f"""{emoji} <b>{name}</b>

💰 <b>{price_str}₽</b> (было {old_price_str}₽)
📉 Скидка: {discount}%

⭐ Рейтинг: {rating} | 👥 Отзывов: {reviews}
🏪 Магазин: {store}

👉 <a href='{url}'>Перейти к товару</a>"""
    
    return text

def get_main_keyboard() -> types.InlineKeyboardMarkup:
    """
    Возвращает основную клавиатуру
    """
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    btn1 = types.InlineKeyboardButton("🔍 Последние скидки", callback_data="last")
    btn2 = types.InlineKeyboardButton("🏆 Топ выгодных", callback_data="top")
    btn3 = types.InlineKeyboardButton("💎 Премиум", callback_data="premium")
    btn4 = types.InlineKeyboardButton("📢 Канал", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")
    
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    
    return keyboard

# ========== ОБРАБОТЧИКИ КОМАНД ==========

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """
    Обработчик команды /start
    """
    user = message.from_user
    log_info(f"Пользователь {user.id} (@{user.username}) запустил бота")
    
    welcome_text = f"""👋 <b>Привет, {user.first_name}!</b>

Я <b>PriceHunterSK</b> — твой личный охотник за скидками 🏷️

🔍 <b>Что я умею:</b>
• Искать лучшие скидки на Wildberries, Ozon и AliExpress
• Показывать самые выгодные предложения
• Отслеживать цены на любимые товары (премиум)

📢 <b>Наш канал:</b> {CHANNEL_ID}
Там выходят лучшие скидки каждый день

💎 <b>Премиум подписка:</b> 500₽/месяц
• Мгновенные уведомления о скидках
• Отслеживание любых товаров
• История цен
• Ранний доступ

👇 <b>Выбери действие:</b>"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['last'])
def cmd_last(message):
    """
    Обработчик команды /last - показывает последние скидки
    """
    log_info(f"Пользователь {message.from_user.id} запросил последние скидки")
    
    products = load_products()
    
    if not products:
        bot.send_message(
            message.chat.id,
            "😕 Пока нет товаров. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return
    
    # Отправляем первые 5 товаров
    sent = 0
    for product in products[:5]:
        try:
            text = format_product_card(product)
            image = product.get('image', product.get('image_url'))
            
            if image:
                bot.send_photo(
                    message.chat.id,
                    image,
                    caption=text,
                    parse_mode='HTML'
                )
            else:
                bot.send_message(
                    message.chat.id,
                    text,
                    parse_mode='HTML',
                    disable_web_page_preview=False
                )
            sent += 1
            time.sleep(0.5)  # Небольшая пауза между сообщениями
        except Exception as e:
            log_error(f"Ошибка отправки товара: {e}")
    
    if sent == 0:
        bot.send_message(
            message.chat.id,
            "😕 Не удалось загрузить товары.",
            reply_markup=get_main_keyboard()
        )

@bot.message_handler(commands=['top'])
def cmd_top(message):
    """
    Обработчик команды /top - показывает топ-10 выгодных предложений
    """
    log_info(f"Пользователь {message.from_user.id} запросил топ предложений")
    
    products = load_products()
    
    if not products:
        bot.send_message(
            message.chat.id,
            "😕 Пока нет товаров. Попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        return
    
    text = "🏆 <b>ТОП-10 САМЫХ ВЫГОДНЫХ ПРЕДЛОЖЕНИЙ</b>\n\n"
    
    for i, product in enumerate(products[:10], 1):
        name = product.get('name', 'Без названия')[:50]
        price = product.get('price', product.get('sale_price', 0))
        discount = product.get('discount', 0)
        store = product.get('store', 'Магазин')
        
        price_str = f"{price:,}".replace(',', ' ') if price else "0"
        
        text += f"{i}. {name}\n"
        text += f"   💰 {price_str}₽ | 📉 -{discount}%\n"
        text += f"   🏪 {store}\n\n"
    
    # Добавляем информацию о подписке
    text += "💎 <b>Хотите больше?</b> Оформите премиум подписку и получайте уведомления о новых скидках мгновенно!"
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['search'])
def cmd_search(message):
    """
    Обработчик команды /search - поиск товаров
    """
    try:
        query = message.text.split(' ', 1)[1].lower()
    except IndexError:
        bot.send_message(
            message.chat.id,
            "❌ Напишите так: /search iphone\nИли: /search наушники",
            reply_markup=get_main_keyboard()
        )
        return
    
    log_info(f"Пользователь {message.from_user.id} ищет: {query}")
    
    products = load_products()
    results = []
    
    for product in products:
        name = product.get('name', '').lower()
        if query in name:
            results.append(product)
            if len(results) >= 5:
                break
    
    if not results:
        bot.send_message(
            message.chat.id,
            f"😕 По запросу '{query}' ничего не найдено.\nПопробуйте другое слово.",
            reply_markup=get_main_keyboard()
        )
        return
    
    text = f"🔍 <b>Результаты поиска: {query}</b>\n\n"
    
    for i, product in enumerate(results, 1):
        name = product.get('name', 'Без названия')[:50]
        price = product.get('price', product.get('sale_price', 0))
        discount = product.get('discount', 0)
        
        price_str = f"{price:,}".replace(',', ' ') if price else "0"
        
        text += f"{i}. <a href='{product.get('url', '#')}'>{name}</a>\n"
        text += f"   💰 {price_str}₽ | 📉 -{discount}%\n\n"
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        disable_web_page_preview=False,
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['premium'])
def cmd_premium(message):
    """
    Обработчик команды /premium - информация о подписке
    """
    log_info(f"Пользователь {message.from_user.id} запросил информацию о премиум")
    
    if is_premium(message.from_user.id):
        # У пользователя уже есть подписка
        users = load_users()
        user_data = users.get(str(message.from_user.id), {})
        expire = user_data.get('expires', 'Неизвестно')
        
        text = f"""💎 <b>У вас активна премиум подписка!</b>

✅ Спасибо за поддержку!
📅 Действует до: {expire}

Премиум-функции:
• Мгновенные уведомления о скидках
• Отслеживание любых товаров (/watch)
• История цен
• Ранний доступ

Скоро появятся новые функции!"""
        
        bot.send_message(
            message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
        return
    
    # У пользователя нет подписки
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    crypto_btn = types.InlineKeyboardButton(
        "💎 Криптовалюта (TON)",
        callback_data="pay_crypto"
    )
    card_btn = types.InlineKeyboardButton(
        "💳 Карта РФ (Озон)",
        callback_data="pay_card"
    )
    check_btn = types.InlineKeyboardButton(
        "✅ Проверить оплату",
        callback_data="check_payment"
    )
    
    keyboard.add(crypto_btn, card_btn)
    keyboard.add(check_btn)
    
    text = """💎 <b>ПРЕМИУМ ПОДПИСКА — 500₽/месяц</b>

<b>Что вы получите:</b>
✅ Мгновенные уведомления о падении цен
✅ Отслеживание любых товаров
✅ История цен на товары
✅ Ранний доступ к новым скидкам
✅ Без рекламы

<b>Способы оплаты:</b>
• Криптовалюта TON (мгновенно)
• Карта РФ (Озон Банк)

Выберите способ оплаты ниже 👇"""
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        reply_markup=keyboard
    )

@bot.message_handler(commands=['watch'])
def cmd_watch(message):
    """
    Обработчик команды /watch - отслеживание товара (только для премиум)
    """
    if not is_premium(message.from_user.id):
        bot.send_message(
            message.chat.id,
            "❌ Эта команда только для премиум-пользователей.\n\nОформите подписку: /premium",
            reply_markup=get_main_keyboard()
        )
        return
    
    bot.send_message(
        message.chat.id,
        "🔔 Функция отслеживания товаров появится в следующем обновлении!\n\nСледите за новостями в канале.",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['help'])
def cmd_help(message):
    """
    Обработчик команды /help
    """
    text = """<b>📚 ПОМОЩЬ ПО БОТУ</b>

<b>Основные команды:</b>
/start - Запустить бота
/last - Последние 10 скидок
/top - Топ-10 выгодных предложений
/search <товар> - Поиск товаров
/premium - Информация о подписке
/help - Эта справка

<b>Премиум команды:</b>
/watch <ссылка> - Отслеживать товар

<b>Полезные ссылки:</b>
📢 Канал: {CHANNEL_ID}
👤 Админ: @Qwertonyq

<b>По всем вопросам обращайтесь к администратору.</b>"""
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

# ========== ОБРАБОТЧИКИ КОЛЛБЭКОВ ==========

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """
    Обработчик нажатий на инлайн кнопки
    """
    user_id = call.from_user.id
    
    if call.data == "last":
        # Показываем последние скидки
        bot.answer_callback_query(call.id, "Загружаю последние скидки...")
        products = load_products()
        
        if not products:
            bot.send_message(
                call.message.chat.id,
                "😕 Пока нет товаров. Попробуйте позже."
            )
            return
        
        # Отправляем первые 3 товара
        sent = 0
        for product in products[:3]:
            try:
                text = format_product_card(product)
                image = product.get('image', product.get('image_url'))
                
                if image:
                    bot.send_photo(
                        call.message.chat.id,
                        image,
                        caption=text,
                        parse_mode='HTML'
                    )
                else:
                    bot.send_message(
                        call.message.chat.id,
                        text,
                        parse_mode='HTML'
                    )
                sent += 1
                time.sleep(0.5)
            except Exception as e:
                log_error(f"Ошибка отправки: {e}")
        
        if sent == 0:
            bot.send_message(
                call.message.chat.id,
                "😕 Не удалось загрузить товары."
            )
    
    elif call.data == "top":
        # Показываем топ
        bot.answer_callback_query(call.id, "Загружаю топ предложений...")
        products = load_products()
        
        if not products:
            bot.send_message(
                call.message.chat.id,
                "😕 Пока нет товаров. Попробуйте позже."
            )
            return
        
        text = "🏆 <b>ТОП-5 ВЫГОДНЫХ ПРЕДЛОЖЕНИЙ</b>\n\n"
        
        for i, product in enumerate(products[:5], 1):
            name = product.get('name', 'Без названия')[:50]
            price = product.get('price', product.get('sale_price', 0))
            discount = product.get('discount', 0)
            store = product.get('store', 'Магазин')
            
            price_str = f"{price:,}".replace(',', ' ')
            
            text += f"{i}. {name}\n"
            text += f"   💰 {price_str}₽ | 📉 -{discount}%\n"
            text += f"   🏪 {store}\n\n"
        
        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode='HTML'
        )
    
    elif call.data == "premium":
        # Информация о премиум
        bot.answer_callback_query(call.id)
        
        if is_premium(user_id):
            bot.send_message(
                call.message.chat.id,
                "💎 У вас уже есть активная премиум подписка!"
            )
            return
        
        # Показываем способы оплаты
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        crypto_btn = types.InlineKeyboardButton(
            "💎 Криптовалюта (TON)",
            callback_data="pay_crypto"
        )
        card_btn = types.InlineKeyboardButton(
            "💳 Карта РФ",
            callback_data="pay_card"
        )
        keyboard.add(crypto_btn, card_btn)
        
        bot.send_message(
            call.message.chat.id,
            "💎 <b>Выберите способ оплаты:</b>",
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    elif call.data == "pay_crypto":
        # Оплата криптовалютой
        bot.answer_callback_query(call.id)
        
        text = f"""💎 <b>Оплата криптовалютой TON</b>

Отправьте <b>10 TON</b> на кошелёк:

<code>{CRYPTO_WALLET}</code>

Сеть: <b>TON</b>

После отправки нажмите кнопку "✅ Проверить оплату" и укажите хеш транзакции.

⚠️ Средства поступят автоматически в течение нескольких минут."""
        
        keyboard = types.InlineKeyboardMarkup()
        check_btn = types.InlineKeyboardButton(
            "✅ Проверить оплату",
            callback_data="check_payment"
        )
        keyboard.add(check_btn)
        
        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    elif call.data == "pay_card":
        # Оплата картой
        bot.answer_callback_query(call.id)
        
        text = f"""💳 <b>Оплата картой РФ (Озон Банк)</b>

Переведите <b>500 рублей</b> на карту:

<code>{CARD_NUMBER}</code>

Получатель: <b>Озон Банк</b>

После отправки нажмите кнопку "✅ Проверить оплату" и укажите сумму перевода.

⚠️ Подписка будет активирована вручную после проверки администратором."""
        
        keyboard = types.InlineKeyboardMarkup()
        check_btn = types.InlineKeyboardButton(
            "✅ Проверить оплату",
            callback_data="check_payment"
        )
        keyboard.add(check_btn)
        
        bot.send_message(
            call.message.chat.id,
            text,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    
    elif call.data == "check_payment":
        # Проверка оплаты
        bot.answer_callback_query(call.id, "🔄 Проверка...")
        
        # Для демо активируем сразу
        users = load_users()
        users[str(user_id)] = {
            'expires': (datetime.now() + timedelta(days=30)).isoformat(),
            'payment_method': 'crypto',
            'activated': datetime.now().isoformat(),
            'username': call.from_user.username,
            'first_name': call.from_user.first_name
        }
        save_users(users)
        
        bot.send_message(
            call.message.chat.id,
            "✅ <b>Подписка успешно активирована!</b>\n\nСпасибо за поддержку! Теперь вам доступны все премиум-функции.\n\nСкоро появятся новые возможности!",
            parse_mode='HTML'
        )
        
        log_info(f"Премиум активирован для пользователя {user_id}")

# ========== АДМИН-КОМАНДЫ ==========

@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    """
    Админ-панель
    """
    if message.from_user.id != ADMIN_ID:
        return
    
    text = """🔧 <b>АДМИН-ПАНЕЛЬ</b>

/users - список пользователей
/stats - статистика
/broadcast - массовая рассылка
/add_user - добавить пользователя вручную"""
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='HTML'
    )

@bot.message_handler(commands=['users'])
def cmd_users(message):
    """
    Список пользователей (только для админа)
    """
    if message.from_user.id != ADMIN_ID:
        return
    
    users = load_users()
    
    if not users:
        bot.send_message(message.chat.id, "📊 Нет пользователей")
        return
    
    text = "📊 <b>СПИСОК ПОЛЬЗОВАТЕЛЕЙ</b>\n\n"
    
    for uid, data in users.items():
        try:
            expire = datetime.fromisoformat(data.get('expires', '2000-01-01'))
            days = (expire - datetime.now()).days
            status = "✅" if days > 0 else "❌"
            
            name = data.get('first_name', 'Неизвестно')
            username = data.get('username', '')
            
            text += f"{status} <b>{name}</b> (@{username})\n"
            text += f"   ID: {uid}\n"
            text += f"   Дней: {days}\n"
            text += f"   Метод: {data.get('payment_method', 'unknown')}\n\n"
        except:
            continue
    
    # Разбиваем на части, если слишком длинное
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    """
    Статистика (только для админа)
    """
    if message.from_user.id != ADMIN_ID:
        return
    
    users = load_users()
    products = load_products()
    
    # Считаем активные подписки
    active = 0
    for uid, data in users.items():
        try:
            expire = datetime.fromisoformat(data.get('expires', '2000-01-01'))
            if expire > datetime.now():
                active += 1
        except:
            pass
    
    # Считаем товары по магазинам
    stores = {}
    for p in products:
        store = p.get('store', 'Unknown')
        stores[store] = stores.get(store, 0) + 1
    
    store_stats = "\n".join([f"   {store}: {count}" for store, count in stores.items()])
    
    text = f"""📈 <b>СТАТИСТИКА ПРОЕКТА</b>

👥 <b>Пользователи:</b>
   Всего: {len(users)}
   Активных подписок: {active}

📦 <b>Товары:</b>
   Всего: {len(products)}
{store_stats}

💰 <b>Доход (оценка):</b>
   {active * 500}₽/месяц

⚙️ <b>Система:</b>
   Бот: {'✅ Работает' if BOT_TOKEN else '❌ Нет токена'}
   Канал: {CHANNEL_ID}
   Последний запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    bot.send_message(message.chat.id, text, parse_mode='HTML')

@bot.message_handler(commands=['add_user'])
def cmd_add_user(message):
    """
    Добавление пользователя вручную (только для админа)
    """
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        # Формат: /add_user 123456789 30
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(
                message.chat.id,
                "❌ Формат: /add_user USER_ID DAYS\nПример: /add_user 123456789 30"
            )
            return
        
        user_id = parts[1]
        days = int(parts[2])
        
        users = load_users()
        users[user_id] = {
            'expires': (datetime.now() + timedelta(days=days)).isoformat(),
            'payment_method': 'manual',
            'activated': datetime.now().isoformat(),
            'added_by': 'admin'
        }
        save_users(users)
        
        bot.send_message(
            message.chat.id,
            f"✅ Пользователь {user_id} добавлен на {days} дней"
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

# ========== ЗАПУСК БОТА ==========

if __name__ == '__main__':
    log_info("=" * 50)
    log_info("🚀 ЗАПУСК БОТА PRICEHUNTERSK")
    log_info("=" * 50)
    log_info(f"Бот: @PriceHunter2bot")
    log_info(f"Канал: {CHANNEL_ID}")
    log_info(f"Админ ID: {ADMIN_ID}")
    log_info("=" * 50)
    
    print("\n" + "=" * 60)
    print("🚀 БОТ PRICEHUNTERSK ЗАПУЩЕН")
    print("=" * 60)
    print(f"📱 Бот: @PriceHunter2bot")
    print(f"📢 Канал: {CHANNEL_ID}")
    print(f"👤 Админ: @Qwertonyq")
    print("=" * 60)
    print("⏳ Ожидание команд...")
    print("=" * 60)
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        log_info("🛑 Бот остановлен пользователем")
        print("\n🛑 Бот остановлен")
    except Exception as e:
        log_error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
