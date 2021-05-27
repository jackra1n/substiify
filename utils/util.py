from utils.store import store
from datetime import datetime
from pytz import timezone
from pathlib import Path
import coloredlogs
import logging
import json

def prepareFiles():

    keyword = 'file'

    default_settings = {
        "token": "",
        "version": "0.6"
    }

    # Prepare logging 
    date = datetime.now(timezone('Europe/Zurich')).strftime('%Y-%m-%d')
    coloredlogs.install()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename=f'{store.logs_path}/{date}.log', encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
    logger.addHandler(handler)

    # Create 'logs' folder if it doesn't exist
    Path('logs').mkdir(parents=True, exist_ok=True)

    # Create 'settings.json' if it doesn't exist
    if not Path(store.settings_path).is_file():
        logging.info(f'{keyword} | Creating {store.settings_path}')
        with open(store.settings_path, 'a') as f:
            json.dump(default_settings, f, indent=2)

    # Create database file if it doesn't exist
    if not Path(store.db_path).is_file():
        logging.info(f'{keyword} | Creating {store.db_path}')
        open(store.db_path, 'a')

    logging.info(f'{keyword} | All files ready')

# if bot is 'substiffy alpha' change prefix
def prefix(bot, message):
    return prefixById(bot)

def prefixById(bot):
    if bot.user.id == 742380498986205234:
        return "dev<<"
    return "<<"