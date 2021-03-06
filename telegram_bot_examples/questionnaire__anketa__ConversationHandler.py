#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import os
import time

# pip install python-telegram-bot
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext, ConversationHandler
from telegram.ext.dispatcher import run_async

import config
from common import get_logger, log_func, reply_error


BUTTON_START_ANKETA = 'Заполнить анкету'
REPLY_KEYBOARD_MARKUP = ReplyKeyboardMarkup(
    [[BUTTON_START_ANKETA]], resize_keyboard=True
)
REPLY_KEYBOARD_MARKUP_SET_RATING = ReplyKeyboardMarkup(
    [["1", "2", "3", "4", "5"]],
    resize_keyboard=True, one_time_keyboard=True
)

STATE_USER_NAME = 'user_name'
STATE_USER_AGE = 'user_age'
STATE_RATING = 'rating'
STATE_COMMENT = 'comment'

ANKETA_TEXT_FORMAT = """\
Результат опроса:
    <b>Имя:</b> {name}
    <b>Возраст:</b> {age}
    <b>Оценка:</b> {rating}
    <b>Комментарий:</b> {comment}
"""


log = get_logger(__file__)


@run_async
@log_func(log)
def on_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите что-нибудь', reply_markup=REPLY_KEYBOARD_MARKUP
    )


@run_async
@log_func(log)
def on_anketa_start(update: Update, context: CallbackContext):
    context.user_data['name'] = ''
    context.user_data['age'] = ''
    context.user_data['rating'] = ''
    context.user_data['comment'] = ''

    update.message.reply_text('Как вас зовут?', reply_markup=ReplyKeyboardRemove())
    return STATE_USER_NAME


@run_async
@log_func(log)
def on_anketa_set_name(update: Update, context: CallbackContext):
    context.user_data['name'] = update.message.text

    update.message.reply_text("Сколько вам лет?")
    return STATE_USER_AGE


@run_async
@log_func(log)
def on_anketa_set_age(update: Update, context: CallbackContext):
    context.user_data['age'] = update.message.text

    update.message.reply_text(
        "Оцените статью от 1 до 5",
        reply_markup=REPLY_KEYBOARD_MARKUP_SET_RATING
    )
    return STATE_RATING


@run_async
@log_func(log)
def on_anketa_set_rating(update: Update, context: CallbackContext):
    context.user_data['rating'] = update.message.text

    update.message.reply_text(
        "Напишите отзыв или нажмите кнопку пропустить этот шаг.",
        reply_markup=ReplyKeyboardMarkup(
            [["Пропустить"]],
            resize_keyboard=True, one_time_keyboard=True
        )
    )
    return STATE_COMMENT


@run_async
@log_func(log)
def on_anketa_comment(update: Update, context: CallbackContext):
    context.user_data['comment'] = update.message.text
    text = ANKETA_TEXT_FORMAT.format(**context.user_data)

    update.message.reply_html(text)
    update.message.reply_text(
        "Спасибо вам за комментарий!", reply_markup=REPLY_KEYBOARD_MARKUP
    )

    return ConversationHandler.END


@run_async
@log_func(log)
def on_anketa_exit_comment(update: Update, context: CallbackContext):
    text = ANKETA_TEXT_FORMAT.format(**context.user_data)

    update.message.reply_html(text)
    update.message.reply_text("Спасибо!", reply_markup=REPLY_KEYBOARD_MARKUP)

    return ConversationHandler.END  # выходим из диалог


@run_async
@log_func(log)
def on_anketa_invalid_set_rating(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Я вас не понимаю, выберите оценку на клавиатуре!',
        reply_markup=REPLY_KEYBOARD_MARKUP_SET_RATING
    )


@run_async
@log_func(log)
def on_request(update: Update, context: CallbackContext):
    message = update.message

    message.reply_text(
        'Echo: ' + message.text,
        reply_markup=REPLY_KEYBOARD_MARKUP
    )


def on_error(update: Update, context: CallbackContext):
    reply_error(log, update, context)


def main():
    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug('System: CPU_COUNT=%s, WORKERS=%s', cpu_count, workers)

    log.debug('Start')

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(
        config.TOKEN,
        workers=workers,
        use_context=True
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', on_start))

    dp.add_handler(
        ConversationHandler(
            entry_points=[MessageHandler(Filters.regex(BUTTON_START_ANKETA), on_anketa_start)],
            states={
                STATE_USER_NAME: [MessageHandler(Filters.text, on_anketa_set_name)],
                STATE_USER_AGE: [MessageHandler(Filters.text, on_anketa_set_age)],
                STATE_RATING: [MessageHandler(Filters.regex('1|2|3|4|5'), on_anketa_set_rating)],
                STATE_COMMENT: [
                    MessageHandler(Filters.regex('Пропустить'), on_anketa_exit_comment),
                    MessageHandler(Filters.text, on_anketa_comment)
                ],
            },
            fallbacks=[
                MessageHandler(
                    Filters.text | Filters.video | Filters.photo | Filters.document, on_anketa_invalid_set_rating
                )
            ]
        )
    )

    dp.add_handler(MessageHandler(Filters.text, on_request))

    # Handle all errors
    dp.add_error_handler(on_error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

    log.debug('Finish')


if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            log.exception('')

            timeout = 15
            log.info(f'Restarting the bot after {timeout} seconds')
            time.sleep(timeout)
