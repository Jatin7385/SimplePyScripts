#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from flask import Flask, jsonify, redirect, request
app = Flask(__name__)


@app.route('/')
def index():
    # return "Тут ничего нет интересного"
    return redirect('/get_news_list?last=15')


@app.route('/get_news_list', defaults={'interest': None})
@app.route('/get_news_list/<interest>')
def get_news_list(interest=None):
    """
    Функция возвращает новости.

    :param interest:
    :return:

    """

    last = request.args.get('last')
    if last:
        last = int(last)

    from common import get_news_list
    news_list, total = get_news_list(interest, last)

    from collections import defaultdict
    interest_by_news_list = defaultdict(list)

    for title, url, interest in news_list:
        interest_by_news_list[interest].append({
            'title': title,
            'url': url,
        })

    return jsonify({
        'items': interest_by_news_list,
        'count': len(news_list),
        'total': total,
    })


@app.route('/get_news_list_and_mark_as_read', defaults={'interest': None})
@app.route('/get_news_list_and_mark_as_read/<interest>')
def get_news_list_and_mark_as_read(interest=None):
    """
    Функция возвращает непрочитанные еще новости и помечает их как помеченные.

    :param interest:
    :return:
    """

    count = request.args.get('count')
    if count:
        count = int(count)

    from common import get_news_list_and_mark_as_read
    news_list, total = get_news_list_and_mark_as_read(interest, count)

    from collections import defaultdict
    interest_by_news_list = defaultdict(list)

    for title, url, interest in news_list:
        interest_by_news_list[interest].append({
            'title': title,
            'url': url,
        })

    return jsonify({
        'items': interest_by_news_list,
        'count': len(news_list),
        'total': total,
    })


@app.route('/reset_all_is_read')
def reset_all_is_read():
    """
    Функция сбрасывает у всех новостей флаг is_read -- то, что они прочитаны.

    :return:
    """

    from common import reset_all_is_read
    reset_all_is_read()

    return jsonify({'status': 'ok'})


if __name__ == "__main__":
    app.debug = True

    # Localhost
    app.run(
        # Включение поддержки множества подключений
        threaded=True,
    )

    # # Public IP
    # app.run(host='0.0.0.0')
