# pylint: disable=W0614
from .json_base import *

class Sponsor(JsonBase):

    def __init__(self, text:str=None):
        self.address = None
        self.total_promo = 0
        super().__init__(text)