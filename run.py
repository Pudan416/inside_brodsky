import asyncio
import logging
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Add this import
from config.settings import settings
from handlers.handlers import register_handlers


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Create a memory storage for FSM
    storage = MemoryStorage()

    # Инициализация и запуск бота
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # Регистрация обработчиков
    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())