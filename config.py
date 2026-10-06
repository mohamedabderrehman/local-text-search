"""One configuration source; relative paths resolve from this application."""
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
def path(name, default):
    value = Path(os.getenv(name, default))
    return value if value.is_absolute() else BASE_DIR / value
DATABASE_PATH = path('DATABASE_PATH', 'data/search.db')
CORPUS_DIR = path('CORPUS_DIR', 'data/corpus')
RESULTS_DIR = path('RESULTS_DIR', 'data/results')
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '100000'))
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
FLASK_DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY') or os.urandom(32)
ENABLE_TELEGRAM = os.getenv('ENABLE_TELEGRAM', '0') == '1'
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')
SESSION_TIMEOUT = 3600
