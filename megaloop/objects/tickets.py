# pylint: disable=W0614
from .consts import *
from .ticket import *
from .json_dict import *

class Tickets(JsonDictDB):
    
    def save(self, ticket:Ticket):
        self[ticket.address] = ticket

    def __init__(self, db:IconScoreDatabase, draw_number:str):
        super().__init__(f'{TICKETS_DICT}_{draw_number}', db, Ticket)