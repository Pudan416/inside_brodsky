import random
import pickle
import os
from pathlib import Path
from games.base_game import BaseGame
from config.settings import settings


class RoomGame(BaseGame):
    """Игра 'Не выходи из комнаты' по мотивам стихотворения Бродского"""

    name = "Не выходи из комнаты"
    poem = "Не выходи из комнаты"
    description = "Исследуйте границы внутреннего мира, не выходя из комнаты"

    def __init__(self, user_id: int):
        super().__init__(user_id)
        # Инициализация элементов игры
        self.exits = {
            "окно": "Вид на улицу, где жизнь кажется обманчиво интересной",
            "дверь": "Выход в мир, полный людей с лицами, как крупа",
            "телефон": "Связь с внешним миром, который меняет пространство и время",
        }
        self.objects = {
            "шипка": {"description": "Пачка сигарет 'Шипка'", "uses": 20},
            "мебель": {
                "description": "Деревянная мебель, не отличимая от людей снаружи",
                "uses": None,
            },
            "книга": {
                "description": "Книга, в которой слова складываются в строчки",
                "uses": None,
            },
            "бумага": {
                "description": "Лист бумаги для создания собственной вселенной",
                "uses": 100,
            },
        }
        self.internal_cosmos = 0  # Уровень развития внутреннего мира
        self.time_passed = 0  # Время, проведенное в комнате
        self.mistake_counter = 0  # Счетчик попыток выйти
        self.thoughts = []  # Записанные мысли
        self.is_aging = True  # Процесс старения

    def save_game_state(self) -> str:
        """Create a compact string representation of game state"""
        # Format: room|internal_cosmos|time_passed|state|is_aging|mistake_counter
        state_parts = [
            "room",
            str(self.internal_cosmos),
            str(self.time_passed),
            self.state,
            "1" if self.is_aging else "0",
            str(self.mistake_counter),
        ]

        # Add object states with a different delimiter
        obj_parts = []
        for obj_name, obj_data in self.objects.items():
            if obj_data["uses"] is not None:
                obj_parts.append(f"{obj_name}={obj_data['uses']}")

        # Add the object state as a single part
        state_parts.append(",".join(obj_parts))

        # Join the main state with a pipe delimiter
        main_state = "|".join(state_parts)

        # Add thoughts with a completely separate section
        if self.thoughts:
            # Join thoughts with a different delimiter
            thought_section = "§".join(self.thoughts)
            return f"{main_state}#THOUGHTS#{thought_section}"
        else:
            return main_state

    @classmethod
    def load_from_state_string(cls, user_id: int, state_string: str) -> "RoomGame":
        """Recreate game state from compact string"""
        game = cls(user_id)

        if not state_string or not state_string.startswith("room"):
            return game

        # Split thoughts section from main state
        if "#THOUGHTS#" in state_string:
            main_state, thoughts_section = state_string.split("#THOUGHTS#", 1)
            # Parse thoughts
            game.thoughts = thoughts_section.split("§")
        else:
            main_state = state_string

        # Split main state parts
        parts = main_state.split("|")

        if len(parts) >= 7:
            game.internal_cosmos = int(parts[1])
            game.time_passed = int(parts[2])
            game.state = parts[3]
            game.is_aging = parts[4] == "1"
            game.mistake_counter = int(parts[5])

            # Parse object states
            obj_states = parts[6].split(",")
            for obj_state in obj_states:
                if "=" in obj_state:
                    obj_name, uses_str = obj_state.split("=", 1)
                    if obj_name in game.objects:
                        game.objects[obj_name]["uses"] = int(uses_str)

        return game

    def write_thought(self, thought: str) -> str:
        """Записать мысль"""
        print(f"Writing thought: '{thought}', current state: {self.state}")

        if "бумага" not in self.objects or self.objects["бумага"]["uses"] <= 0:
            self.state = "normal"
            return "У тебя нет бумаги для записи мыслей."

        # Store only the thought text
        self.thoughts.append(thought)

        print(f"Thoughts after adding: {self.thoughts}")

        self.objects["бумага"]["uses"] -= 1
        self.internal_cosmos += 5
        self.time_passed += 1
        self.state = "normal"

        return f'Ты записал: "{thought}". Твой внутренний космос растёт.'

    def process_command(self, command: str) -> str:
        """Обработка команды игрока"""
        command = command.lower().strip()

        # Если игра завершена
        if self.state == "game_over":
            return "Игра окончена. Введи /start для начала новой игры."

        # Если в режиме записи мысли
        if self.state == "writing":
            result = self.write_thought(command)
            return result

        # Обработка команд
        if command == "осмотреться":
            return self.look_around()
        elif command == "размышлять":
            return self.reflect()
        elif command.startswith("выйти"):
            parts = command.split(" ", 1)
            exit_name = parts[1] if len(parts) > 1 else "дверь"
            return self.try_exit(exit_name)
        elif command.startswith("использовать"):
            parts = command.split(" ", 1)
            item_name = parts[1] if len(parts) > 1 else ""
            return self.use_object(item_name)
        elif command == "мысли":
            return self.view_thoughts()
        elif command == "старение":
            return self.toggle_aging()
        elif command == "помощь":
            return self.get_help()
        else:
            return "Я не понимаю. Введи 'помощь' для списка доступных команд."

    def look_around(self) -> str:
        """Осмотреть комнату"""
        description = "\nТы находишься в комнате. Твоём пространстве. Твоей вселенной."
        description += "\n\nВыходы:"
        for exit_name, exit_desc in self.exits.items():
            description += f"\n- {exit_name}: {exit_desc}"

        description += "\n\nПредметы:"
        for obj_name, obj_data in self.objects.items():
            details = (
                f" (осталось {obj_data['uses']})"
                if obj_data["uses"] is not None
                else ""
            )
            description += f"\n- {obj_name}: {obj_data['description']}{details}"

        description += f"\n\nВнутренний мир: {self.internal_cosmos} очков"
        description += f"\nВремя в комнате: {self.time_passed} часов"

        return description

    def try_exit(self, exit_name: str) -> str:
        """Попытка выйти из комнаты"""
        if exit_name not in self.exits:
            return "Такого выхода нет. Хотя, возможно, это и к лучшему."

        self.mistake_counter += 1

        responses = [
            "Не выходи из комнаты, не совершай ошибку.",
            "За дверью бессмысленно все, особенно — возглас счастья.",
            "Только в уборную — и сразу же возвращайся.",
            "О, не выходи из комнаты. Танцуй, поймав, боссанову...",
            "...в пальто на голое тело, в туфлях на босу ногу.",
        ]

        if self.mistake_counter >= 5:
            self.state = "game_over"
            return "Ты вышел из комнаты. Поздравляю, ты совершил ошибку.\nКОНЕЦ ИГРЫ.\n\nВведи /start, чтобы начать новую игру."

        return random.choice(responses)

    def use_object(self, object_name: str) -> str:
        """Использовать предмет в комнате"""
        if object_name not in self.objects:
            return "Такого предмета нет в комнате."

        object_data = self.objects[object_name]

        if object_name == "шипка":
            if object_data["uses"] <= 0:
                return "Сигареты закончились. Зачем тебе Солнце, если ты больше не куришь Шипку?"

            object_data["uses"] -= 1
            self.time_passed += 1
            return "Ты куришь Шипку. Зачем тебе Солнце, если ты куришь Шипку?"

        elif object_name == "мебель":
            self.time_passed += 1
            return "Мебель точь-в-точь как люди, и вообще инвентарь."

        elif object_name == "книга":
            self.internal_cosmos += 5
            self.time_passed += 3
            return "В книге слова складываются в строчки, и вокруг них — пробелы."

        elif object_name == "бумага":
            if object_data["uses"] <= 0:
                return "Бумага закончилась. Возможно, это знак приближения к концу."

            self.state = "writing"
            return "Ты берешь лист бумаги. Напиши свою мысль в следующем сообщении..."

        return "Ты используешь этот предмет, но ничего особенного не происходит."

    def reflect(self) -> str:
        """Размышлять о жизни"""
        self.internal_cosmos += 3
        self.time_passed += 2

        reflections = [
            "В комнате лучше. Никто не валтузит сапогом фарфоровые черепки.",
            "Не выходи из комнаты; считай, что в ней тебя хватит.",
            "Не выходи из комнаты; о, пускай только комната догадывается...",
            "...что ты внутри нее, как стук сердца.",
            "Зачем выходить из комнаты? На улице, чай, не Франция.",
        ]

        return random.choice(reflections)

    def write_thought(self, thought: str) -> str:
        """Записать мысль"""
        if "бумага" not in self.objects or self.objects["бумага"]["uses"] <= 0:
            self.state = "normal"
            return "У тебя нет бумаги для записи мыслей."

        # Store only the thought text
        self.thoughts.append(thought)

        self.objects["бумага"]["uses"] -= 1
        self.internal_cosmos += 5
        self.time_passed += 1
        self.state = "normal"

        return f'Ты записал: "{thought}". Твой внутренний космос растёт.'

    def view_thoughts(self) -> str:
        """Просмотреть записанные мысли"""
        if not self.thoughts:
            return "Ты еще не записал ни одной мысли."

        result = "Твои мысли:"
        for i, thought in enumerate(self.thoughts):
            result += f"\n{i+1}. {thought}"

        return result

    def toggle_aging(self) -> str:
        """Включить/выключить процесс старения"""
        self.is_aging = not self.is_aging

        if self.is_aging:
            return "Ты снова подвержен процессу старения."
        else:
            return "В комнате старение замедляется — не то, что снаружи."

    def check_special_ending(self) -> bool:
        """Проверить условие для специальной концовки"""
        if self.internal_cosmos >= 100:
            self.state = "game_over"
            return True
        return False

    def check_time_ending(self) -> bool:
        """Проверить условие для концовки по времени"""
        if self.time_passed > 150:
            self.state = "game_over"
            return True
        return False

    def get_special_ending(self) -> str:
        """Получить текст особой концовки"""
        return """
╔=================╗
║  ОСОБАЯ КОНЦОВКА   ║
╚=================╝

Твой внутренний космос расширился до такой степени,
что комната уже не может сдерживать его.

Не выходи из комнаты. Запрись и забаррикадируйся
шкафом от хроноса, космоса, эроса, расы, вируса...

Ты понимаешь, что уже не комната удерживает тебя,
а ты удерживаешь комнату внутри своего сознания.

То, что считалось тюрьмой, стало вселенной.
Пространство внутри бесконечно больше пространства снаружи.

ПОЗДРАВЛЯЕМ!
Ты достиг истинного понимания стихотворения Бродского.

Введи /start, чтобы начать новую игру.
"""

    def get_time_ending(self) -> str:
        """Получить текст концовки по времени"""
        return """
Жизнь подходит к концу. Вечность обретается лишь в слове.
КОНЕЦ ИГРЫ.

Введи /start, чтобы начать новую игру.
"""

    def get_help(self) -> str:
        """Получить справку по игре"""
        return """
📜 Доступные команды:
- осмотреться - осмотреть комнату
- размышлять - предаться размышлениям
- выйти дверь/окно/телефон - попытаться выйти
- использовать шипка/мебель/книга/бумага - использовать предмет
- мысли - просмотреть записанные мысли
- старение - включить/выключить процесс старения
- помощь - показать список команд

🎮 Цель игры: развить свой внутренний космос до 100 очков, не выходя из комнаты.
"""

    def get_intro(self) -> str:
        """Получить вступление к игре"""
        return """
╔=================╗
║:::::::НЕ ВЫХОДИ ::::::::║
║::::::ИЗ КОМНАТЫ:::::::║
║————————————║
║.....игра по мотивам....║
║::::::стихотворения::::::║
║::::::::::Бродского:::::::::║
║————————————║
║:::автор @pudan416::::║
╚=================╝

Не выходи из комнаты, не совершай ошибку.
Зачем тебе Солнце, если ты куришь Шипку?

Ты находишься в комнате. В своем внутреннем мире.
Исследуй границы пространства внутри себя.

Введи "помощь", чтобы увидеть список доступных команд.
"""
