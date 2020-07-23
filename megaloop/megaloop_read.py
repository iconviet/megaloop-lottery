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
        return str(player) if player else None
    
    @external(readonly=True)
    def get_last_winner(self) -> str:
        winner = self._winners.get_last()
        return str(winner) if winner else None

    @external(readonly=True)
    def get_last_draw(self) -> str:
        last_draw = self._draws.get_last()
        return str(last_draw) if last_draw else None

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        ticket = self._tickets.get_last()
        if ticket:
            open_draw = self._open_draw
            ticket.chance = ticket.amount / open_draw.prize
            return str(ticket)

    @external(readonly=True)
    def get_past_draws(self, skip:int, take:int, desc:bool) -> str:
        if skip and take and desc:
            return self.__in_range_order(self._draws, skip, take, desc)

    @external(readonly=True)
    def get_past_winners(self, skip:int, take:int, desc:bool) -> str:
        if skip and take and desc:
            return self.__in_range_order(self._winners, skip, take, desc)

    @external(readonly=True)
    def get_players(self, skip:int, take:int, desc:bool) -> str:
        if skip and take and desc:
            return self.__in_range_order(self._players, skip, take, desc)

    @external(readonly=True)
    def get_sponsors(self, skip:int, take:int, desc:bool) -> str:
        if skip and take and desc:
            return self.__in_range_order(self._sponsors, skip, take, desc)

    @external(readonly=True)
    def get_tickets(self, skip:int, take:int, desc:bool) -> str:
        if skip and take and desc:
            open_draw = self._open_draw
            def work(ticket:Ticket):
                ticket.chance = ticket.amount / open_draw.prize
                return ticket
            return self.__in_range_order(self._tickets, skip, take, desc, work)

    @external(readonly=True)
    def get_past_tickets(self, draw_number:str, skip:int, take:int, desc:bool) -> str:
        if skip and take and desc:
            tickets = Tickets(self._db, draw_number)
            return [str(ticket) for ticket in tickets]

    def __in_range_order(self, json_dict:JsonDictDB, skip:int, take:int, desc:bool, work=None) -> list:
        sign = 1
        if desc:
            sign = -1
            skip += 1
        take = abs(skip) + take
        def lazy(json:JsonBase):
            return json
        func = lazy if not work else work
        if take == 0: return [str(i) for i in json_dict]
        if take >= len(json_dict): take = len(json_dict) + 1
        return [str(func(json_dict.get(i * sign))) for i in range(skip, take)]