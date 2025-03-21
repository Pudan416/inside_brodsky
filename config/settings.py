import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка .env файла
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    SAVE_DIR: str = os.getenv("SAVE_DIR", "data/saves")
    
    # Убедимся, что директория для сохранений существует
    def __init__(self):
        save_dir = Path(__file__).parent.parent / self.SAVE_DIR
        save_dir.mkdir(parents=True, exist_ok=True)  # Добавляем parents=True

settings = Settings()