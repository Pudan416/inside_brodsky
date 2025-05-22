from aiogram import Dispatcher, Bot, types
from aiogram.filters import Command
from typing import Dict, Optional
from games import AVAILABLE_GAMES
from games.base_game import BaseGame
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# Словари для хранения состояний пользователей
user_games: Dict[int, BaseGame] = {}  # user_id -> игра
user_temp_states: Dict[int, Dict] = {}  # Для сохранения временных состояний (вне игры)


def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_exit, Command("exit"))
    dp.message.register(handle_messages)  # Обработчик обычных сообщений


async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    """Обработчик команды /start - автоматический запуск игры "Не выходи из комнаты" """
    user_id = message.from_user.id

    # Clear user state
    await state.clear()
    
    # Очищаем временное состояние
    if user_id in user_temp_states:
        del user_temp_states[user_id]

    # Если пользователь был в игре, удаляем её
    if user_id in user_games:
        del user_games[user_id]

    # Автоматически создаем игру "Не выходи из комнаты"
    from games.room import RoomGame
    game = RoomGame(user_id)
    print(f"Created game: {RoomGame.__name__}")

    # Store reference for current session
    user_games[user_id] = game

    # Get initial game state
    initial_state = game.save_game_state()
    print(f"Initial game state: {initial_state}")

    # Update state - store initial game state
    await state.update_data(
        selecting=False,
        game_state=initial_state,
        game_type=RoomGame.__name__,
    )

    # Send game intro
    await bot.send_message(chat_id=message.chat.id, text=game.get_intro())


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
    
    # Очищаем все состояния пользователя
    if user_id in user_games:
        del user_games[user_id]
    if user_id in user_temp_states:
        del user_temp_states[user_id]

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
    game_state = state_data.get("game_state", None)
    
    # Debug information
    print(f"User {user_id} message: '{text}'")
    print(f"Game state: {game_state}")

    # If user has an active game
    if game_state:
        game = None

        # Поддерживаем только игру "Не выходи из комнаты"
        if game_state.startswith("room"):
            from games.room import RoomGame
            game = RoomGame.load_from_state_string(user_id, game_state)
            print(f"Loaded RoomGame with state: {game.state}")
        else:
            # Если состояние от другой игры, сбрасываем и создаем новую RoomGame
            from games.room import RoomGame
            game = RoomGame(user_id)
            print("Created new RoomGame due to incompatible state")

        # Process command
        print(f"Processing command '{text}' with game state: {game.state}")
        result = game.process_command(text)
        print(f"Command result: {result[:50]}...")
        print(f"After processing, game state: {game.state}")

        # Update the game instance
        user_games[user_id] = game

        # Save the updated game state
        new_game_state = game.save_game_state()
        print(f"New saved game state: {new_game_state}")
        await state.update_data(game_state=new_game_state)

        # Check for endings
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
        # User isn't in a game - automatically start RoomGame
        await cmd_start(message, state, bot)