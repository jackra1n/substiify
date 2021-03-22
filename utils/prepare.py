import json
from utils.store import store
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

    if not Path(store.settings_path).is_file():
        log(f'Creating {store.settings_path}\n', keyword)
        with open(store.settings_path, 'a') as f:
            json.dump(default_settings, f, indent=2)

    log('All files setup', keyword)
