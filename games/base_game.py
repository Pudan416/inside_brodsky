from abc import ABC, abstractmethod
from pathlib import Path
import pickle
from config.settings import settings  # Импортируем настройки из вашего модуля


class BaseGame(ABC):
    """Базовый класс для всех игр"""
    
    # Остальной код...


class BaseGame(ABC):
    """Базовый класс для всех игр"""

    # Имя игры и произведение
    name: str = "Базовая игра"
    poem: str = "Произведение Бродского"
    description: str = "Описание игры"

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.state = "normal"  # Состояние игры (normal, special_state, game_over)

    @abstractmethod
    def process_command(self, command: str) -> str:
        """Обработка команды пользователя"""
        pass

    @abstractmethod
    def get_help(self) -> str:
        """Получить справку по игре"""
        pass

    @abstractmethod
    def get_intro(self) -> str:
        """Получить вступление к игре"""
        pass

    @classmethod
    def get_short_description(cls) -> str:
        """Получить краткое описание игры для выбора"""
        return f"{cls.name} (по мотивам '{cls.poem}'): {cls.description}"

    def save_game_state(self, game_folder: str) -> None:
        """Базовый метод для сохранения состояния игры"""
        save_dir = Path(settings.SAVE_DIR) / game_folder
        save_dir.mkdir(parents=True, exist_ok=True)

        save_path = save_dir / f"{self.user_id}.pickle"
        try:
            with open(save_path, "wb") as f:
                pickle.dump(self, f)
        except Exception as e:
            print(f"Ошибка при сохранении игры {game_folder}: {e}")
