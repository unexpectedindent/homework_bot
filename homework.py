import logging
import logging.config
import sys
import time
from http import HTTPStatus

import requests
import telegram

from config import (ENDPOINT, HEADERS, HOMEWORK_STATUSES,
                    LOGGING_CONFIG, RETRY_TIME,
                    PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)
from exceptions import ResponseContentError


logger = logging.getLogger(__name__)


def send_message(bot: telegram.Bot, message: str) -> None:
    """Send message into Telegram chat."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Message is sent')
    except telegram.error.TelegramError:
        raise telegram.error.TelegramError('Sending message is failed')


def get_api_answer(current_timestamp: int) -> dict:
    """Get info about homeworks statuses."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    logger.debug('Try make request to API')
    response = requests.get(
        url=ENDPOINT,
        params=params,
        headers=HEADERS
    )
    if response.status_code == HTTPStatus.OK:
        logger.debug('Response from server is gotten')
        try:
            return response.json()
        except AttributeError:
            raise AttributeError(
                'Response doesnt contain data in json format'
            )
    else:
        raise ConnectionError('Connection with server is failed')


def check_response(response: dict) -> list:
    """Checks response from server."""
    if isinstance(response, dict):
        logger.debug('Response contains dictionary')
        if isinstance(response.get('homeworks'), list):
            logger.debug('Response contains data')
            if len(response['homeworks']):
                logger.debug('Response contains valid data')
                return response.get('homeworks')
            logger.warning('Response contains empty data')
        raise ResponseContentError('Response doesnt contain homeworks data')
    raise TypeError(f'Response type: {type(response).__name__}')


def parse_status(homework: dict) -> str:
    """Generate message with task status."""
    homework_name = homework.get('homework_name')
    if not homework_name:
        raise KeyError('Data doesnt contain info about task name')
    homework_status = homework.get('status')
    if not homework_status:
        raise KeyError('Data doesnt contain info about task status')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Check the tokens."""
    return all((
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ))


def main() -> None:
    """Base bot logic."""
    if not check_tokens():
        tokens = {
            'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
        }
        for token_name, token in tokens.items():
            if not token:
                logger.critical(f'{token_name} failure')
        sys.exit('Incorrect token(s)')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    homework_state = {}
    while True:
        logger.debug('Circles start')
        try:
            response = get_api_answer(current_timestamp - RETRY_TIME)
            for homework in check_response(response):
                if homework_state.get(homework['id']) != homework['status']:
                    homework_state[homework['id']] = homework['status']
                    send_message(bot, parse_status(homework))
                else:
                    logger.debug('No status change')
        except Exception as error:
            logger.exception(f'Program failed: {error}')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_CONFIG)
    main()
