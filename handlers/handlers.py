from aiogram import Dispatcher, Bot, types
from aiogram.filters import Command
from typing import Dict, Optional
from games import AVAILABLE_GAMES
from games.base_game import BaseGame
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Словари для хранения состояний пользователей
user_games: Dict[int, BaseGame] = {}  # user_id -> игра


def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_exit, Command("exit"))
    dp.message.register(handle_messages)  # Обработчик обычных сообщений


async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    """Обработчик команды /start - выбор игры"""
    user_id = message.from_user.id

    # Clear user state
    await state.clear()

    # Отмечаем, что пользователь в режиме выбора игры
    await state.update_data(selecting=True)

    # Если пользователь был в игре, удаляем её
    if user_id in user_games:
        del user_games[user_id]

    # Формируем список доступных игр
    menu_text = "Добро пожаловать в мир поэзии Иосифа Бродского!\nЧтобы выбрать игру, напишите её номер:\n"

    # Используем доступные игры из импортированного списка
    for i, game_class in enumerate(AVAILABLE_GAMES, 1):
        menu_text += f"\n{i}. {game_class.name} ('{game_class.poem}')"
        if hasattr(game_class, "description"):
            menu_text += f" - {game_class.description}"

    # Отправляем только одно сообщение с меню
    await bot.send_message(chat_id=message.chat.id, text=menu_text)


async def cmd_help(message: types.Message, bot: Bot):
    """Обработчик команды /help - показать общую справку"""
    help_text = """
📚 Привет, это Костя. 
Ко дню рождения Иосифа Александровича Бродскогото я сделал серию из несколькиз текстовых игр по мотивам моих любимых его произведений!

Основные команды этого бота:
/start - Выбрать игру или начать новую
/help - Показать эту справку
/exit - Выйти из текущей игры

Внутри каждой игры доступны свои команды. Чтобы узнать какие – напишите "помощь" во время игры.

Из уважения к поэту всё управление в играх происходит через написание слов. Никаких кнопок, как в старых добрых текстовых квестах.

Если хотите купить мне кофе 
"""
    await bot.send_message(chat_id=message.chat.id, text=help_text)


async def cmd_exit(message: types.Message, state: FSMContext, bot: Bot):
    """Обработчик команды /exit - выход из игры"""
    user_id = message.from_user.id
    if user_id in user_games:
        del user_games[user_id]

    # Clear the state
    await state.clear()

    await bot.send_message(
        chat_id=message.chat.id,
        text="Вы вышли из игры. Введите /start, чтобы выбрать новую.",
    )


async def handle_messages(message: types.Message, state: FSMContext, bot: Bot):
    """Обработчик обычных сообщений"""
    if not message.text:
        return

    user_id = message.from_user.id
    text = message.text.strip()

    # Get current state data
    state_data = await state.get_data()
    selecting = state_data.get("selecting", False)
    game_state = state_data.get("game_state", None)
    game_type = state_data.get("game_type", "")

    # Debug information
    print(f"User {user_id} message: '{text}'")
    print(f"State data: {state_data}")
    print(f"Selecting: {selecting}, Game type: {game_type}")

    # If user is selecting a game
    if selecting:
        try:
            game_index = int(text) - 1
            print(
                f"User selected game index: {game_index}, available games: {len(AVAILABLE_GAMES)}"
            )

            # Check if it's one of the placeholder games
            if game_index >= len(AVAILABLE_GAMES):
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Эта игра пока в разработке. Пожалуйста, выберите доступную игру.",
                )
                return

            # Check if index is in valid range
            if 0 <= game_index < len(AVAILABLE_GAMES):
                # Create new game
                game_class = AVAILABLE_GAMES[game_index]
                game = game_class(user_id)
                print(f"Created game: {game_class.__name__}")

                # Store reference for current session
                user_games[user_id] = game

                # Get initial game state
                initial_state = game.save_game_state()
                print(f"Initial game state: {initial_state}")

                # Update state - no longer selecting, store initial game state
                await state.update_data(
                    selecting=False,
                    game_state=initial_state,
                    game_type=game_class.__name__,
                )

                # Send game intro
                await bot.send_message(chat_id=message.chat.id, text=game.get_intro())
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Неверный выбор. Пожалуйста, выберите игру из списка.",
                )
        except ValueError as e:
            print(f"ValueError during game selection: {str(e)}")
            await bot.send_message(
                chat_id=message.chat.id,
                text="Пожалуйста, введите номер игры из списка.",
            )
        return

    # If user has an active game
    # Код для замены части функции handle_messages в handlers.py

# Если user has an active game
    elif game_state:
        game = None

        # Debug the game state format
        print(f"Game state format check: '{game_state[:20]}...'")

        # Определяем тип игры по префиксу состояния
        if game_state.startswith("room"):
            from games.room import RoomGame
            game = RoomGame.load_from_state_string(user_id, game_state)
            print(f"Loaded RoomGame with state: {game.state}")
        elif game_state.startswith("odysseus"):
            from games.odysseus import OdysseusGame
            game = OdysseusGame.load_from_state_string(user_id, game_state)
            print(f"Loaded OdysseusGame with state: {game.state}")
            # Дополнительная отладка для игры Одиссей
            print(f"OdysseusGame current location: {game.current_location}")
            print(f"OdysseusGame wisdom: {game.wisdom}, homesickness: {game.homesickness}")
        elif game_state.startswith("roman"):
            from games.roman_friend import RomanFriendGame
            game = RomanFriendGame.load_from_state_string(user_id, game_state)
            print(f"Loaded RomanFriendGame with state: {game.state}")

        # If no game was loaded, handle error
        if game is None:
            print("Failed to load or create a game")
            await bot.send_message(
                chat_id=message.chat.id,
                text="Ошибка загрузки игры. Введите /start, чтобы начать сначала.",
            )
            return

        # Process command with extra debug
        print(f"Processing command '{text}' with game state: {game.state}")
        result = game.process_command(text)
        print(f"Command result: {result[:50]}...")  # Print first 50 chars of result
        print(f"After processing, game state: {game.state}")

        # Update the game instance in the user_games dictionary
        user_games[user_id] = game

        # Save the updated game state before checking endings
        new_game_state = game.save_game_state()
        print(f"New saved game state: {new_game_state}")
        await state.update_data(game_state=new_game_state)

        # Check for special endings
        if game.check_special_ending():
            result = game.get_special_ending()
            # Clear game state to start fresh
            await state.clear()
        elif game.check_time_ending():
            result = game.get_time_ending()
            # Clear game state to start fresh
            await state.clear()

        # Send result
        await bot.send_message(chat_id=message.chat.id, text=result)
    else:
        # User isn't in a game and isn't selecting
        await bot.send_message(
            chat_id=message.chat.id,
            text="Вы не в игре. Введите /start, чтобы выбрать игру.",
        )