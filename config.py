import os

# Telegram настройки
BOT_TOKEN = os.getenv('BOT_TOKEN', '8647325049:AAE5ZnLj-qeApz9BvQOlFkRlk8YN8rb6onw')
CHANNEL_ID = '@PriceHunterSK'  # Название твоего канала
ADMIN_ID = 7687644925  # Твой Telegram ID

# imgbb для картинок
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', 'e3c23045e2db5ab742f182365a63b675')

# Платежные данные
CRYPTO_WALLET = 'UQDJxx5UWzanMN_9Yb8iFVsia4-f0z0pembHtIFSdcOPqseZ'  # TON кошелек
CARD_NUMBER = '2204 3206 4195 8311'  # Карта Озон

# Настройки парсинга
PARSING_INTERVAL = 6  # часов
MAX_PRODUCTS_PER_STORE = 50  # максимум товаров с одного магазина
