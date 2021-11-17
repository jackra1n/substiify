from helper.CustomLogFormatter import CustomLogFormatter
from logging.handlers import TimedRotatingFileHandler
from utils.store import store
from pathlib import Path

import logging
import json

ignore_logs = [
    'Got a request',
]

class RemoveNoise(logging.Filter):
    def __init__(self):
        super().__init__(name='discord.gateway')

    def filter(self, record):
        if (record.name == 'discord.gateway' and 'Shard ID' in record.msg) or any(log in record.msg for log in ignore_logs):
            return False
        return True

def prepareFiles():

    default_settings = {
        "token": "",
        "version": "0.6"
    }

    # Create 'logs' folder if it doesn't exist
    Path('logs').mkdir(parents=True, exist_ok=True)

    # Create 'data' folder if it doesn't exist
    Path('data').mkdir(parents=True, exist_ok=True)

    # Filter out some of the logs that come from discord.gateway
    logging.getLogger('discord.gateway').addFilter(RemoveNoise())

    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    fileFormatter = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}', dt_fmt, style='{')

    fileHandler = TimedRotatingFileHandler(f'{store.logs_path}/substiify_', when="midnight", interval=1, encoding='utf-8')
    fileHandler.suffix = "%Y-%m-%d.log"
    fileHandler.setFormatter(fileFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(CustomLogFormatter())
    rootLogger.addHandler(consoleHandler)

    logger = logging.getLogger('util.prepare_files')

    # Create 'settings.json' if it doesn't exist
    if not Path(store.settings_path).is_file():
        logger.info(f'Creating {store.settings_path}')
        with open(store.settings_path, 'a') as f:
            json.dump(default_settings, f, indent=2)

    # Create database file if it doesn't exist
    if not Path(store.db_path).is_file():
        logger.info(f'Creating {store.db_path}')
        open(store.db_path, 'a')

    logger.info(f'All files ready')
