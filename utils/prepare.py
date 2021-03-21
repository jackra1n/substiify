import json
from pathlib import Path
from utils.logger import log

def createFiles():

    keyword = 'file'

    default_settings = {
        "prefix": "<<",
        "token": "",
        "version": "0.6"
    }

    # Create 'logs' folder if it doesn't exist
    Path('logs').mkdir(parents=True, exist_ok=True)

    if not Path('./data/settings.json').is_file():
        log('Creating settings.json\n', keyword)
        with open('./data/settings.json', 'a') as f:
            json.dump(default_settings, f, indent=2)

    log('All files setup', keyword)
