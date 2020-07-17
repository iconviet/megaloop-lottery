# pylint: disable=W0614
from .json_base import *

class Draw(JsonBase):
    
    def __init__(self, json:str=None):
        self.block = 0
        self.prize = 0 
        self.promo = 0
        self.number = None
        self.winner = None
        self.timestamp = 0
        self.block_count = 0
        self.ticket_count = 0
        self.payout_ratio = 0
        self.seeding_limit = 0
        self.revenue_limit = 0
        super().__init__(json)
    
    @property
    def total(self):
        return float(self.prize + self.promo)

    @property
    def revenue(self):
        return float(self.total - self.payout)

    @property
    def payout(self):
        return float(self.total * self.payout_ratio)