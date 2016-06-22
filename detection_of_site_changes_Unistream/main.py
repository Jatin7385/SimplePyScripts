#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import sys

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(filename)s[LINE:%(lineno)d] %(levelname)-8s %(message)s',
    handlers=[
        logging.FileHandler('log', encoding='utf8'),
        logging.StreamHandler(stream=sys.stdout),
    ],
)


def get_site_text(url='https://test.api.unistream.com/help/index.html'):
    """Функция возвращает содержимое по указанному url."""

    import sys

    from PySide.QtGui import QApplication
    from PySide.QtCore import QEventLoop
    from PySide.QtWebKit import QWebSettings, QWebPage, QWebView
    from PySide.QtNetwork import QNetworkProxyFactory

    # Чтобы не было проблем запуска компов с прокси:
    QNetworkProxyFactory.setUseSystemConfiguration(True)

    QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

    class WebPage(QWebPage):
        def userAgentForUrl(self, url):
            return 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'

    if QApplication.instance() is None:
        QApplication(sys.argv)

    view = QWebView()
    view.setPage(WebPage())
    view.load(url)

    # Ждем пока прогрузится страница
    loop = QEventLoop()
    view.loadFinished.connect(loop.quit)
    loop.exec_()

    doc = view.page().mainFrame().documentElement()
    print(len(doc.toOuterXml()), len(doc.toPlainText()))
    return doc.toPlainText()
    # return doc.toOuterXml()


def get_hash_from_str(text):
    """Функция возвращает хеш от строки в виде HEX чисел, используя алгоритм sha1."""

    import hashlib
    alg = hashlib.sha1()
    alg.update(text.encode())
    return alg.hexdigest().upper()


def get_diff(str_1, str_2, full=True):
    """
    Функция сравнивает переданные строки и возвращает результат сравнения в html.

    """

    # from diff_match_patch import diff_match_patch
    #
    # # open('str1', 'w', encoding='utf-8').write(str_1)
    # # open('str2', 'w', encoding='utf-8').write(str_2)
    # # import os
    # # os.system('kdiff3 str1 str2')
    #
    # diff = diff_match_patch()
    # diffs = diff.diff_main(str_1, str_2)
    # diff_html = diff.diff_prettyHtml(diffs)
    #
    # print(diffs)
    # print(len(diffs))
    # quit()

    logging.debug('x1')
    import difflib

    logging.debug('x2')
    diff_html = ""
    logging.debug('x3')
    theDiffs = difflib.ndiff(str_1.splitlines(), str_2.splitlines())

    logging.debug('x4')
    for eachDiff in theDiffs:
        logging.debug('  x5')
        if eachDiff[0] == "-":
            diff_html += "<del>%s</del><br>" % eachDiff[1:].strip()
        elif eachDiff[0] == "+":
            diff_html += "<ins>%s</ins><br>" % eachDiff[1:].strip()
    logging.debug('x5')

    if full:
        return """<html><head><meta charset="utf-8"></head> <body>""" + diff_html + "</body></html>"
    else:
        return diff_html

    # # from lxml.html.diff import htmldiff
    # # return """<html><head>
    # #     <meta charset="utf-8">
    # # </head> <body>""" + htmldiff(str_1, str_2) + "</body></html>"

    # open('str1', 'w', encoding='utf-8').write(str_1)
    # open('str2', 'w', encoding='utf-8').write(str_2)

    # logging.debug('x1')
    # str_lines_1 = str_1.splitlines()
    # str_lines_2 = str_2.splitlines()
    # logging.debug('x2')
    # # print(len(str_lines_1), len(str_lines_2))
    # # print(str_lines_1[:5], str_lines_2[:5])
    #
    # from difflib import HtmlDiff
    # diff = HtmlDiff()
    #
    # # # diff умеет работать с списками, поэтому строку нужно разбить на списки строк,
    # # # например, построчно:
    # # if full:
    # #     return diff.make_file(str_lines_1, str_lines_2)
    # # else:
    # #     return diff.make_table(str_lines_1, str_lines_2)
    #
    # return """<html><head>
    #     <meta charset="utf-8">
    # </head> <body>""" + diff.make_table(str_lines_1, str_lines_2) + "</body></html>"


from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class TextRevision(Base):
    """
    Класс описывает таблицу ревизий текста.
    Новая запись в таблице появляется только если предыдущая запись имеет отличия от новой.

    """

    __tablename__ = 'TextRevision'

    id = Column(Integer, primary_key=True)

    text = Column(String)

    # Хеш текста
    text_hash = Column(String)

    # Дата проверки
    datetime = Column(DateTime)

    # Поле описывает разницу с предыдущей ревизией.
    # Содержимым является полноценная html страница
    diff_full = Column(String)

    # Поле описывает разницу с предыдущей ревизией.
    # Содержимым является только разница
    diff = Column(String)

    def __init__(self, text, other_text=''):
        """
        Конструктор принимает контент и сравниваемый контент, запоминает хеш содержимого,
        текущую дату и время и результат сравнения

        """

        from datetime import datetime

        self.text = text
        self.text_hash = get_hash_from_str(text)
        self.datetime = datetime.today()
        self.diff_full = get_diff(text, other_text)
        self.diff = get_diff(text, other_text, full=False)

    def __repr__(self):
        return "<TextRevision(id: {}, datetime: {}, text_hash: {})>".format(self.id, self.datetime, self.text_hash)


def get_session():
    import os
    DIR = os.path.dirname(__file__)
    DB_FILE_NAME = 'sqlite:///' + os.path.join(DIR, 'database')
    # DB_FILE_NAME = 'sqlite:///:memory:'

    # Создаем базу, включаем логирование и автообновление подключения каждые 2 часа (7200 секунд)
    from sqlalchemy import create_engine
    engine = create_engine(
        DB_FILE_NAME,
        # echo=True,
        pool_recycle=7200
    )

    Base.metadata.create_all(engine)

    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()


session = get_session()


def get_last_revision():
    """Функция возвращает последнуюю запись в таблице TextRevision."""

    return session.query(TextRevision).order_by(TextRevision.id.desc()).first()


def add_text_revision(text):
    """Функция добавляет новую ревизию, предварительно сравнив ее с предыдущей."""

    last = get_last_revision()
    logging.debug('Последняя запись: %s.', last)

    text_revision = None

    # Если таблица пуста
    if last is None:
        text_revision = TextRevision(text)
    else:
        # Если хеши текстов отличаются, добавляем новую ревизию
        if last.text_hash != get_hash_from_str(text):
            logging.debug('Обнаружено изменение, создаю ревизию.')
            text_revision = TextRevision(text, last.text)
            logging.debug('-')
        else:
            logging.debug('Одинаковые значения, пропускаю добавление.')
            return

    logging.debug('@')
    if text_revision:
        logging.debug('add')
        session.add(text_revision)
        logging.debug('commit')
        session.commit()

    logging.debug('return')
    return text_revision


if __name__ == '__main__':
    logging.debug('Запуск.')

    import time

    while True:
        try:
            logging.debug('Проверка сайта.')
            text = get_site_text()

            # У сайта есть особенность -- некоторые данные в примерах с каждой загрузки
            # новые, и они портят работу скрипта, но не несут никакой пользы
            # Нужно их удалить.
            # Данные:
            # "OperationId": "ab0ddd72-767d-400c-b17c-811c88c2cdc1",
            # "CommandId": "c4a52a43-8caf-4f51-bcd3-8090fb91b597",
            # "cashierUniqueId": "cc3b8fe2-8ecc-4af4-9076-d5315aa74896",
            # "id": "31f7e9e2-ea4f-469a-a498-379cfcc3fa12",
            # "createTime": "2016-06-22T10:13:42.0888396+03:00",
            import re
            text = re.sub(r'"((?i)OperationId)": ".+?"', r'"\1": "<removed>"', text)
            text = re.sub(r'"((?i)CommandId)": ".+?"', r'"\1": "<removed>"', text)
            text = re.sub(r'"((?i)cashierUniqueId)": ".+?"', r'"\1": "<removed>"', text)
            text = re.sub(r'"((?i)id)": ".+?"', r'""\1"": "<removed>"', text)
            text = re.sub(r'"((?i)createTime)": ".+?"', r'"\1": "<removed>"', text)

            add_text_revision(text)
            logging.debug('Проверка закончена.')

            # Задержка каждые 7 часов
            time.sleep(60 * 60 * 7)
        except Exception:
            logging.exception('Error:')

    last = get_last_revision()
    print(len(last.text))
    if last:
        open('diff.html', 'w', encoding='utf-8').write(last.diff_full)
