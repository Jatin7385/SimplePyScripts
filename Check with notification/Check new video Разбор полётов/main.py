#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


"""
Скрипт для уведомления о появлении новых видео Разбора полётов.

"""


# Чтобы можно было импортировать all_common.py, находящийся уровнем выше
import sys
sys.path.append('..')

# Чтобы импортировать функцию для получения списка видео
sys.path.append('../../html_parsing')

from all_common import make_backslashreplace_console, run_notification_job
from youtube_com__get_video_list import get_video_list


make_backslashreplace_console()


def my_get_video_list():
    url = 'https://www.youtube.com/playlist?list=PLZfhqd1-Hl3BKhWwCgmqtENSlearqLlAV'
    return get_video_list(url)


if __name__ == '__main__':
    run_notification_job(
        'Check new video Разбор полётов',
        'video',
        my_get_video_list,
        notified_by_sms=True,
        timeout={'days': 1},
        format_current_items='Текущий список видео (%s): %s',
        format_get_items='Запрос видео',
        format_items='Список видео (%s): %s',
        format_new_item='Новое видео "%s"',
        format_no_new_items='Изменений нет',
    )
