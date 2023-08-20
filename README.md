## Проект парсинга pep и документации Python

### Описание
Парсер собирает информацию о версиях Pyton и PEP документацию с сайтов:
- https://docs.python.org/3/
- https://peps.python.org/

Парсер запускается в нескольких режимах через аргументы командной строки

### Инструкция по запуску:
**Клонируйте репозиторий:**
```
git@github.com:Rederickmind/bs4_parser_pep.git
```
**Установите и активируйте виртуальное окружение:**
```
python -m venv venv
source venv/Scripts/activate
```
**Обновите менеджер pip и установите зависимости**
python -m pip install --upgrade pip
pip install -r requirements.txt

**Для запуска парсера перейдите в папку "src":**
```
cd src
```
**Запустите парсер в одном из режимов:**
Справка о режимах парсера
```
python main.py -h
```
Очистить кэш:
```
python main.py <parser_mode> -c
python main.py <parser_mode> --clear-cache
```
Сохранение результатов в CSV файл:
```
python main.py <parser_mode> --output file
```
Отображение результатов в табличном формате в консоли:
```
python main.py <parser_mode> --output pretty
```
```
Если не указывать аргумент --output, результат парсинга будет выведен в консоль кроме парсера download - он загружает архив с документацией в папку downloads
```

### Режимы парсера:
Парсинг последних обновлений с сайта
```
python main.py whats-new <очистка кэша и/или выбор типа вывода>
```

Парсинг последних версий документации
```
python main.py latest_versions <очистка кэша и/или выбор типа вывода>
```

Загрузка и сохранение архива с документацией
```
python main.py download <очистка кэша>
```

Парсинг статусов PEP
```
python main.py pep <очистка кэша и/или выбор типа вывода>
```

**Технологии:**
- Python 3.9.10
- Библиотека BeautifulSoup4
- Библиотека requests-cache
- Библиотека argparse для аргументов командной строки 

### Автор проекта:

Никита Лёвушкин, когорта ЯП 19+