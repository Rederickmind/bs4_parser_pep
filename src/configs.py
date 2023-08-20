import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    # Аргумент для очистки кэша.
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    # Аргумент для выбора способа вывода.
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    # Сформируйте путь до директории logs.
    log_dir = BASE_DIR / 'logs'
    # Создайте директорию.
    log_dir.mkdir(exist_ok=True)
    # Получение абсолютного пути до файла с логами.
    log_file = log_dir / 'parser.log'
    # Инициализация хендлера с ротацией логов.
    # Максимальный объём одного файла — десять в шестой степени байт (10**6),
    # максимальное количество файлов с логами — 5.
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=10 ** 6,
        backupCount=5,
        encoding='utf-8'
    )
    # Базовая настройка логирования basicConfig.
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        # Уровень записи логов.
        level=logging.INFO,
        # Вывод логов в терминал.
        handlers=(rotating_handler, logging.StreamHandler())
    )
