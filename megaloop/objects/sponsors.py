# pylint: disable=W0614
from .consts import *
from .sponsor import *
from .json_dict import *

class Sponsors(JsonDictDB):
    
    def save(self, sponsor:Sponsor):
        self[sponsor.address] = sponsor
    
    def __init__(self, db:IconScoreDatabase):
        super().__init__(SPONSORS_DICT, db, Sponsor)