#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import os
import time
import sys

# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackContext, PicklePersistence
from telegram.ext.dispatcher import run_async

sys.path.append('..')

import config
from common import get_logger, log_func, reply_error


log = get_logger(__file__)


@run_async
@log_func(log)
def on_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Commands: set and get.'
    )


@run_async
@log_func(log)
def on_set(update: Update, context: CallbackContext):
    message = update.message

    end = context.match.span()[1]
    text = message.text[end:].strip()

    context.user_data['text'] = text

    message.reply_text('Saving!')


@run_async
@log_func(log)
def on_get(update: Update, context: CallbackContext):
    message = update.message

    text = context.user_data.get('text', '<Not data, using command set>')

    message.reply_text(
        "get: " + text
    )


@run_async
@log_func(log)
def on_request(update: Update, context: CallbackContext):
    message = update.message

    message.reply_text(
        'Echo: ' + message.text
    )


def on_error(update: Update, context: CallbackContext):
    reply_error(log, update, context)


def main():
    cpu_count = os.cpu_count()
    workers = cpu_count
    log.debug('System: CPU_COUNT=%s, WORKERS=%s', cpu_count, workers)

    log.debug('Start')

    persistence = PicklePersistence(filename='data.pickle')

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(
        config.TOKEN,
        workers=workers,
        persistence=persistence,
        use_context=True
    )

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', on_start))
    dp.add_handler(MessageHandler(Filters.regex(r'(?i)^(set)\b'), on_set))
    dp.add_handler(MessageHandler(Filters.regex(r'(?i)^get'), on_get))
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
