import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, EXPECTED_STATUS, MAIN_PEP_URL
from outputs import control_output
from utils import find_tag, get_response
from exceptions import UNEXPECTED_STATUS, ParserFindTagException


def whats_new(session):
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        # Если основная страница не загрузится, программа закончит работу.
        return
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id. Парсеру нужен только
    # первый элемент, поэтому используется метод find().
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    if not main_div:
        raise ParserFindTagException('Ничего не нашлось')

    # Шаг 2-й: поиск внутри main_div следующего
    # тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    # Шаг 3-й: поиск внутри div_with_ul
    # всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )

    return results


def latest_versions(session):
    # session = requests_cache.CachedSession()
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})

    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
        # Если нужный список не нашёлся,
        # вызывается исключение и выполнение программы прерывается.
        else:
            raise ParserFindTagException('Ничего не нашлось')
    # print(a_tags)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст,
            # второй — пустая строка.
            version, status = a_tag.text, ''
        results.append((link, version, status))

    return results


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    # session = requests_cache.CachedSession()
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    # Получили таблицу с сайта и выбрали нужный регулярным выражением
    table_tag = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    # Сохраняем ссылку на файл
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    # Получаем имя файла из ссылки
    filename = archive_url.split('/')[-1]
    # Создаем дирекиорию загрузки и получаем путь сохранения файла
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    # Загрузка файла
    response = session.get(archive_url)
    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content)
    # Допишите этот код в самом конце функции.
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, MAIN_PEP_URL)
    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'section', {'id': 'numerical-index'})
    pep_list = find_tag(main_tag, 'tbody')
    pep_rows = pep_list.find_all('tr')
    if not pep_rows:
        raise ParserFindTagException('Ничего не нашлось')

    all_pep_count = 0
    logs = []
    temp_results = {}
    results = [('Статус', 'Количество')]
    for pep_row in tqdm(pep_rows):
        list_status = find_tag(pep_row, 'abbr')
        preview_status = list_status.text[1:]
        expected_status = EXPECTED_STATUS[preview_status]

        pep_card_link = find_tag(pep_row, 'a')
        pep_href = pep_card_link['href']
        pep_card_link = urljoin(MAIN_PEP_URL, pep_href)

        response = get_response(session, pep_card_link)
        soup = BeautifulSoup(response.text, 'lxml')
        card_abbr = find_tag(soup, 'abbr')
        pep_card_status = card_abbr.text

        if pep_card_status not in expected_status:
            logs.append(
                UNEXPECTED_STATUS.format(
                 pep_card_link=pep_card_link,
                 pep_card_status=pep_card_status,
                 expected_status=expected_status
                )
            )

        if pep_card_status in temp_results:
            temp_results[pep_card_status] += 1
        else:
            temp_results[pep_card_status] = 1
        all_pep_count += 1
    list(map(logging.warning, logs))
    temp_results['Total'] = all_pep_count
    results += list(temp_results.items())
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')
    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')
    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    # С вызовом функции передаётся и сессия.
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
