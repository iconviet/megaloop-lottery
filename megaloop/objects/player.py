# pylint: disable=W0614
from .json_base import *

class Player(JsonBase):

    def __init__(self, text:str=None):
        self.name = ''
        self.tx_count = 0
        self.timestamp = 0
        self.address = None
        self.total_played = 0
        self.total_payout = 0
        super().__init__(text)