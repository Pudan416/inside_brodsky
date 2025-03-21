from typing import List, Type
from games.base_game import BaseGame
from games.room import RoomGame
from games.odysseus import OdysseusGame 

# Список всех доступных игр
AVAILABLE_GAMES = [
    RoomGame,
    OdysseusGame,
]