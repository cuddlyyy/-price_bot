# Этот файл делает папку parsers модулем Python
from .wildberries import WildberriesParser
from .ozon import OzonParser
from .aliexpress import AliExpressParser

__all__ = ['WildberriesParser', 'OzonParser', 'AliExpressParser']
