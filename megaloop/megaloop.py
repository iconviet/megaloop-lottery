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
from .ticket import *
from .player import *
from .winner import *
from .topper import *
from .config import *
from .drawbox import *
from .instant import *
from .tickets import *
from .players import *
from .winners import *
from .toppers import *
from iconservice import *
from .scorelib.set import *
from .scorelib.iterable_dict import *

class Megaloop(IconScoreBase):    

    @property
    def _instant(self) -> Instant:
        return Instant(self)

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
                
        self._drawbox = DrawBox(db)
        self._tickets = Tickets(db)
        self._players = Players(db)
        self._winners = Winners(db)
        self._toppers = Toppers(db)
        self._config = VarDB(CONFIG_JSON, db, value_type=str)
        
    def on_install(self):
        super().on_install()
        
        topper = self._toppers.create()
        topper.address = str(self.owner)
        self._toppers.save(topper)
        
        config = Config(self._config.get())
        config.draw_topping = to_loop(5)
        config.payout_ratio = to_percent(85)
        self._config.set(str(config))
        
        self._drawbox.open(config, self._instant)

    def on_update(self):
        super().on_update()

        self.draw()

    #######################################################################################

    @payable
    def fallback(self):
        value = self.msg.value
        address = str(self.msg.sender)
        if address in self._toppers: return
        if value:
            try:
                draw = self._drawbox.get_open()
                if draw:
                    draw.total += value
                    self._drawbox.set_open(draw)
                    ticket = self._tickets[address]
                    player = self._players[address]
                    if player:
                        player.total += value
                    else:
                        player =self._players.create()
                        player.total = value
                        player.bh = self._instant.bh
                        player.address = str(address)
                    if ticket:
                        ticket.total += value
                        ticket.bh = self._instant.bh
                    else:
                        ticket = self._tickets.create()
                        ticket.total = value
                        ticket.bh = self._instant.bh
                        ticket.address = str(address)
                    self._players.save(player)
                    self._tickets.save(ticket)
                else:
                    self.icx.transfer(self.msg.sender, self.msg.value)
            except Exception as e:
                revert(f'Megaloop was unable to process your transaction. Error: {str(e)}')
    
    #######################################################################################
    
    @external
    def open(self):
        self._drawbox.open(self._instant, self._config)
    
    @external
    def draw(self):
            try:
                draw = self._drawbox.get_open()
                # balance = self.icx.get_balance(self.address)
                # balance >= draw.payout
                if draw and self._tickets:
                    ticket = draw.random(self, self._tickets)
                    if ticket:    
                        ##############################################
                        config = Config(self._config.get())
                        self._drawbox.close(config, self._instant)
                        ##############################################
                        address = ticket.address
                        winner = self._winners.create()
                        winner.address = address
                        winner.payout = draw.payout
                        winner.bh = self._instant.bh
                        winner.name = self._players[address].name
                        self._winners.save(winner)
                        ##############################################
                        self.icx.transfer(winner.address, draw.payout)
                        ##############################################
            except Exception as e:
                revert(f'Failed to process drawing transaction. Error: {str(e)}')

    #######################################################################################

    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v2.0.0'

    @external(readonly=True)
    def get_config(self) -> str:
        return self._config.get()
    
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
    def get_last_topper(self) -> str:
        topper = self._toppers.get_last()
        return None if not topper else str(topper)

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
    def get_toppers(self) -> str:
        return [str(topper) for topper in self._toppers]