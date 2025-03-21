from aiogram import Dispatcher, Bot, types
from aiogram.filters import Command
from typing import Dict, Optional
from games import AVAILABLE_GAMES
from games.base_game import BaseGame

# Словари для хранения состояний пользователей
user_games: Dict[int, BaseGame] = {}  # user_id -> игра
user_selecting: Dict[int, bool] = {}  # user_id -> выбирает ли игру

def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_exit, Command("exit"))
    dp.message.register(handle_messages)  # Обработчик обычных сообщений

async def cmd_start(message: types.Message, bot: Bot):
    """Обработчик команды /start - выбор игры"""
    user_id = message.from_user.id
    
    # Отмечаем, что пользователь в режиме выбора игры
    user_selecting[user_id] = True
    
    # Если пользователь был в игре, удаляем её
    if user_id in user_games:
        del user_games[user_id]
    
    # Формируем список доступных игр
    menu_text = "Добро пожаловать в мир поэзии Иосифа Бродского!\n\nВыберите игру:\n"
    
    # Добавляем две игры-заглушки
    games_list = AVAILABLE_GAMES.copy()
    games_list.append(type('Game', (), {
        'name': 'Письма римскому другу', 
        'poem': 'Письма римскому другу',
        'description': 'Скоро будет доступно'
    }))
    
    for i, game_class in enumerate(games_list, 1):
        menu_text += f"\n{i}. {game_class.name} ('{game_class.poem}')"
        if hasattr(game_class, 'description'):
            menu_text += f" - {game_class.description}"
    
    await bot.send_message(chat_id=message.chat.id, text=menu_text)

async def cmd_help(message: types.Message, bot: Bot):
    """Обработчик команды /help - показать общую справку"""
    help_text = """
📚 Добро пожаловать в игры по мотивам произведений Бродского!

Команды бота:
/start - Выбрать игру или начать новую
/help - Показать эту справку
/exit - Выйти из текущей игры

Внутри каждой игры доступны свои команды. 
Введите "помощь" во время игры, чтобы увидеть их.
"""
    await bot.send_message(chat_id=message.chat.id, text=help_text)

async def cmd_exit(message: types.Message, bot: Bot):
    """Обработчик команды /exit - выход из игры"""
    user_id = message.from_user.id
    if user_id in user_games:
        del user_games[user_id]
        user_selecting[user_id] = False
        
    await bot.send_message(
        chat_id=message.chat.id, 
        text="Вы вышли из игры. Введите /start, чтобы выбрать новую."
    )

async def handle_messages(message: types.Message, bot: Bot):
    """Обработчик обычных сообщений"""
    if not message.text:
        return
    
    user_id = message.from_user.id
    text = message.text.strip()
    
    # Если пользователь выбирает игру
    if user_id in user_selecting and user_selecting[user_id]:
        try:
            game_index = int(text) - 1
            
            # Проверяем, что это одна из заглушек
            if game_index >= len(AVAILABLE_GAMES):
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Эта игра пока в разработке. Пожалуйста, выберите доступную игру."
                )
                return
                
            # Проверяем, что индекс в допустимом диапазоне
            if 0 <= game_index < len(AVAILABLE_GAMES):
                # Создаем новую игру
                game_class = AVAILABLE_GAMES[game_index]
                game = game_class.load(user_id)
                user_games[user_id] = game
                user_selecting[user_id] = False
                
                # Отправляем вступление к игре
                await bot.send_message(chat_id=message.chat.id, text=game.get_intro())
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="Неверный выбор. Пожалуйста, выберите игру из списка."
                )
        except ValueError:
            await bot.send_message(
                chat_id=message.chat.id,
                text="Пожалуйста, введите номер игры из списка."
            )
        return
    
    # Если пользователь в игре
    if user_id in user_games:
        game = user_games[user_id]
        
        # Обрабатываем команду
        result = game.process_command(text)
        
        # Проверяем, есть ли особые условия завершения
        if game.check_special_ending():
            result = game.get_special_ending()
        elif game.check_time_ending():
            result = game.get_time_ending()
        
        # Сохраняем состояние игры
        game.save()
        
        # Отправляем ответ
        await bot.send_message(chat_id=message.chat.id, text=result)
    else:
        # Если пользователь не в игре и не выбирает игру
        await bot.send_message(
            chat_id=message.chat.id,
            text="Вы не в игре. Введите /start, чтобы выбрать игру."
        )