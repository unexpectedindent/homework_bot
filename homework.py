import logging
import logging.config
import os
import time

import requests
import telegram

from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from exceptions import *
from config import LOGGING_CONFIG

load_dotenv()

logger = logging.getLogger(__name__)


PRACTICUM_TOKEN = os.getenv('YP_TOKEN')
TELEGRAM_TOKEN= os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('ME')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Send message with status update."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except:
        logger.error('Sending message failed')
        raise CanNotSendMessageError('Sending message failed')
    else:
        logger.info('Message is sent')


def get_api_answer(current_timestamp: int) -> dict:
    """Get info about homeworks statuses."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(
        url=ENDPOINT,
        params=params,
        headers=HEADERS
    )
    if response.status_code == 200:
        logger.debug('Response from server is gotten')
        return response.json()
    else:
        logger.debug('Connection with server is failed')
        raise RemoteServerError('Connection with server is failed')


def check_response(response: dict) -> list:
    """Checks """
    if isinstance(response, dict):
        logger.debug('Response contains dictionary')
        if isinstance(response.get('homeworks'), list):
            logger.debug('Response contains data')
            return response.get('homeworks')
        logger.warning('Response is empty')
        raise ResponseContentError('Response doesnt contain homeworks data')
    logger.error(f'Response type: {type(response).__name__}')
    raise TypeError('Incorrect response')


def parse_status(homework: dict) -> str:
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Check the tokens."""
    tokens = (
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    )
    return all(tokens)


def main() -> None:
    """Основная логика работы бота."""
    logging.config.dictConfig(LOGGING_CONFIG)
    if not check_tokens():
        tokens = {
            'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
        }
        for token_name, token in tokens.items():
            if not token:
                logger.critical(f'{token_name} failure')
        raise TokenError
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    homework_state = {}
    while True:
        try:
            response = get_api_answer(current_timestamp - RETRY_TIME)
            for homework in check_response(response):
                if homework_state.get(homework['id']) != homework['status']:
                    homework_state[homework['id']] = homework['status']
                    send_message(bot, parse_status(homework))
        except Exception as error:
            logger.exception(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)
        else:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
