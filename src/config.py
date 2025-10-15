import os
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(project_root, '.env'), override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 1000))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
