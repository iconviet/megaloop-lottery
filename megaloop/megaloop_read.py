# pylint: disable=W0614
from .megaloop_base import *

class MegaloopRead(MegaloopBase):
    
    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v2.0.0'

    @external(readonly=True)
    def get_draw_conf(self) -> str:
        return str(self._draw_conf)

    @external(readonly=True)
    def get_open_draw(self) -> str:
        return str(self._open_draw)

    @external(readonly=True)
    def get_last_player(self) -> str:
        player = self._players.get_last()
        return None if not player else str(player)
    
    @external(readonly=True)
    def get_last_winner(self) -> str:
        winner = self._winners.get_last()
        return None if not winner else str(winner)

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        ticket = self._tickets.get_last()
        if not ticket:
            return None
        open_draw = self._open_draw
        ticket.chance = ticket.amount / open_draw.prize
        return str(ticket)

    @external(readonly=True)
    def get_last_draw(self) -> str:
        last_draw = self._draws.get_last()
        return None if not last_draw else str(last_draw)

    @external(readonly=True)
    def get_past_draws(self, skip:int=0, take:int=0, desc:bool=False) -> str:
        return self.__filter_items_from_json_dict(self._draws, skip, take, desc)

    @external(readonly=True)
    def get_players(self, skip:int=0, take:int=0, desc:bool=False) -> str:
        return self.__filter_items_from_json_dict(self._players, skip, take, desc)

    @external(readonly=True)
    def get_past_winners(self, skip:int=0, take:int=0, desc:bool=False) -> str:
        return self.__filter_items_from_json_dict(self._winners, skip, take, desc)

    @external(readonly=True)
    def get_sponsors(self, skip:int=0, take:int=0, desc:bool=False) -> str:
        return self.__filter_items_from_json_dict(self._sponsors, skip, take, desc)

    @external(readonly=True)
    def get_past_tickets(self, draw_number:str, skip:int=0, take:int=0, desc:bool=False) -> str:
        tickets = Tickets(self._db, draw_number)
        return [str(ticket) for ticket in tickets]

    @external(readonly=True)
    def get_tickets(self, skip:int=0, take:int=0, desc:bool=False) -> str:
        open_draw = self._open_draw
        def calculate_chance(ticket:Ticket):
            ticket.chance = ticket.amount / open_draw.prize
            return ticket
        return self.__filter_items_from_json_dict(self._tickets, skip, take, desc, calculate_chance)

    def __filter_items_from_json_dict(self, json_dict:JsonDictDB, skip:int, take:int, desc:bool, work=None) -> list:
        sign = 1
        if desc:
            sign = -1
            skip -= sign
        take = skip + take
        def slip(json:JsonBase):
            return json
        func = slip if not work else work
        if take > len(json_dict): take = len(json_dict)
        if take == 0: return [str(i) for i in json_dict]
        return [str(func(json_dict.get(i * sign))) for i in range(skip, take)]