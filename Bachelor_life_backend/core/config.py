import os
from dotenv import load_dotenv

# Get the directory where config.py is located, then go up to backend root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=env_path, override=True)

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DATABASE = os.getenv("DATABASE")
DB_PORT = os.getenv("DB_PORT")