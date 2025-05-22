from typing import List, Type
from games.base_game import BaseGame
from games.room import RoomGame
# from games.odysseus import OdysseusGame
# from games.roman_friend import RomanFriendGame

# Список всех доступных игр - оставляем только RoomGame
AVAILABLE_GAMES = [
    RoomGame,
]