# pylint: disable=W0614
from .consts import *
from .winner import *
from .json_dict import *

class Winners(JsonDictDB):
    
    def save(self, winner:Winner):
        self[winner.draw_number] = winner
    
    def __init__(self, db:IconScoreDatabase):
        super().__init__(WINNERS_DICT, db, Winner)