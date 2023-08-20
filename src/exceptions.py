UNEXPECTED_STATUS = (
    '\n Несовпадающие статусы: '
    '\n {pep_card_link} '
    '\n Статус в карточке: {pep_card_status} '
    '\n Ожидаемые статусы: {expected_status} \n '
)


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass
