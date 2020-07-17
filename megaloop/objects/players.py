# pylint: disable=W0614
from .consts import *
from .player import *
from .json_dict import *

class Players(JsonDictDB):
    
    def save(self, player:Player):
        self[player.address] = player

    def __init__(self, db:IconScoreDatabase):
        super().__init__(PLAYERS_DICT, db, Player)