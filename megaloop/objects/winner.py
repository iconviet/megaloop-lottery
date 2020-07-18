# pylint: disable=W0614
from .json_base import *

class Winner(JsonBase):
    def __init__(self, text:str=None):
        self.played = 0
        self.chance = 0
        self.payout = 0
        self.timestamp = 0
        self.address = None
        self.draw_number = None
        super().__init__(text)