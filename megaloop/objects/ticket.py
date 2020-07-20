# pylint: disable=W0614
from .json_base import *

class Ticket(JsonBase):

    def __init__(self, text:str=None):
        self.amount = 0
        self.tx_count = 0
        self.timestamp = 0
        self.address = None
        self.draw_number = None
        super().__init__(text)