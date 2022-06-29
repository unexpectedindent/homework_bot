import os

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILENAME = 'homework_logs.log'

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s, %(levelname)s, %(message)s, %(name)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'extended': {
            'format': (
                '%(asctime)s, '
                '%(filename)s, '
                '%(funcName)s, '
                '%(levelname)s, '
                '%(lineno)d, '
                '%(message)s, '
                '%(name)s'
            ),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'logfile': {
            'formatter': 'extended',
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILENAME,
            'backupCount': 2,
            'maxBytes': 2000000,
            'mode': 'a'
        },
        'stream': {
            'formatter': 'default',
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'homework': {
            'handlers': ['logfile', 'stream'],
            'level': 'DEBUG',

        }
    },
    'root': {'level': 'DEBUG', 'handlers': ['logfile', 'stream']}
}

PRACTICUM_TOKEN = os.getenv('YP_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('ME')

RETRY_TIME = 600

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
