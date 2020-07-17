# pylint: disable=W0614
from .draw import *
from .consts import *
from .json_dict import *

class Draws(JsonDictDB):
    
    def save(self, draw:Draw):
        self[draw.number] = draw

    def __init__(self, db:IconScoreDatabase):
        super().__init__(DRAWS_DICT, db, Draw)

    