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
    def get_past_draws(self) -> str:
        return [str(draw) for draw in self._draws]

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        ticket = self._tickets.get_last()
        if not ticket:
            return None
        open_draw = self._open_draw
        ticket.chance = ticket.amount / open_draw.prize
        return str(ticket)

    @external(readonly=True)
    def get_past_tickets(self, draw_number:str) -> str:
        tickets = Tickets(self._db, draw_number)
        return [str(ticket) for ticket in tickets]
    
    @external(readonly=True)
    def get_last_draw(self) -> str:
        last_draw = self._draws.get_last()
        return None if not last_draw else str(last_draw)

    @external(readonly=True)
    def get_players(self) -> str:
        return [str(player) for player in self._players]
    
    @external(readonly=True)
    def get_past_winners(self) -> str:
        return [str(winner) for winner in self._winners]

    @external(readonly=True)
    def get_sponsors(self) -> str:
        return [str(sponsor) for sponsor in self._sponsors]
    
    @external(readonly=True)
    def get_tickets(self) -> str:
        open_draw = self._open_draw
        def calculate_chance(ticket:Ticket):
            ticket.chance = ticket.amount / open_draw.prize
            return ticket
        return [str(calculate_chance(ticket)) for ticket in self._tickets]