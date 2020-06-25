# -*- coding: utf-8 -*-
#
# Copyright 2020 ICONVIET
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=W0614
from .config import *
from .ticket import *
from .player import *
from .winner import *
from .sponsor import *
from .drawbox import *
from .tickets import *
from .players import *
from .winners import *
from .sponsors import *
from iconservice import *
from .scorelib.set import *
from .scorelib.iterable_dict import *

class Megaloop(IconScoreBase):
        
    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        
        self._config = Config(db)
        self._drawbox = DrawBox(db)
        self._tickets = Tickets(db)
        self._players = Players(db)
        self._winners = Winners(db)
        self._sponsors = Sponsors(db)
        
    def on_install(self):
        super().on_install()
        
        sponsor = self._sponsors.create()
        sponsor.debit = 0
        sponsor.credit = 0
        sponsor.address = str(self.owner)
        self._sponsors.add_or_update(sponsor)

    def on_update(self):
        super().on_update()
        
        self._config.pay_ratio = .85
        self._config.topup_limit = 5
        self._config.prize_limit = 1000
        #self._drawbox.close(self.block_height, 0)
        #self._drawbox.open(self.block_height, 5)

    #######################################################################################

    @payable
    def fallback(self):
        value = self.msg.value
        address = str(self.msg.sender)
        if address in self._sponsors: return
        if value:
            try:
                open_draw = self._drawbox.get_open()
                if open_draw:
                    ticket = self._tickets[address]
                    player = self._players[address]
                    if not ticket:
                        ticket = self._tickets.create()
                        ticket.total = value
                        ticket.address = str(address)
                        ticket.block = self.block_height
                    else:
                        ticket.block = self.block_height
                        ticket.total = ticket.total + value
                    if not player:
                        player =self._players.create()
                        player.total = value
                        player.address = str(address)
                        player.block = self.block_height
                    else:
                        player.total = player.total + value
                    self._tickets.add_or_update(ticket)
                    self._players.add_or_update(player)
                    open_draw.prize = open_draw.prize + value
                    self._drawbox.update_open(open_draw)
                else:
                    self.icx.transfer(self.msg.sender, self.msg.value)
            except Exception as e:
                revert(f'Megaloop was unable to process your transaction. Error: {str(e)}')
    
    #######################################################################################
    
    @external
    def close_draw(self):
        open_draw = self._drawbox.get_open()
        if (open_draw and self._tickets):
            prize = open_draw.total_prize_pay
            if self.icx.get_balance(self.address) < prize:
                revert(f'Insufficient fund. {prize/10**18} ICX required.')
            try:
                ticket = open_draw.get_winning_ticket(self, self._tickets)
                if ticket:    
                    winner = self._winners.create()
                    winner.prize = prize
                    winner.address = ticket.address
                    winner.block = self.block_height
                    self._winners.add_or_update(winner)
                    self.draws.close(self.block_height)
                    self.icx.transfer(ticket.address, prize)
            except Exception as e:
                revert(f'Failed to process transaction. Error: {str(e)}')

    #######################################################################################

    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v2.0.0'

    @external(readonly=True)
    def get_open_draw(self) -> str:
        draw = self._drawbox.get_open()
        return None if not draw else str(draw)
        
    @external(readonly=True)
    def get_last_draw(self) -> str:
        draw = self._drawbox.get_last()
        return None if not draw else str(draw)

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        ticket = self._tickets.get_last()
        return None if not ticket else str(ticket)

    @external(readonly=True)
    def get_last_player(self) -> str:
        player = self._players.get_last()
        return None if not player else str(player)
    
    @external(readonly=True)
    def get_last_winner(self) -> str:
        winner = self._winners.get_last()
        return None if not winner else str(winner)

    @external(readonly=True)
    def get_last_sponsor(self) -> str:
        sponsor = self._sponsors.get_last()
        return None if not sponsor else str(sponsor)

    @external(readonly=True)
    def get_draws(self) -> str:
        return [str(draw) for draw in self._drawbox]

    @external(readonly=True)
    def get_tickets(self) -> str:
        return [str(ticket) for ticket in self._tickets]

    @external(readonly=True)
    def get_players(self) -> str:
        return [str(player) for player in self._players]

    @external(readonly=True)
    def get_winners(self) -> str:
        return [str(winner) for winner in self._winners]

    @external(readonly=True)
    def get_sponsors(self) -> str:
        return [str(sponsor) for sponsor in self._sponsors]