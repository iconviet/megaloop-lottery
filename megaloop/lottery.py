# -*- coding: utf-8 -*-

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
from .draw import *
from .block import *
from .consts import *
from .config import *
from .players import *
from .winners import *
from .jsondict import *

"""
Lottery logic and state management
"""
class Lottery(JsonDictDB):
    
    @property
    def open_draw(self) -> Draw:
        return Draw(self._open_draw.get())
    
    @open_draw.setter
    def open_draw(self, open_draw:Draw):
        self._open_draw.set(str(open_draw))

    def __init__(self, db:IconScoreDatabase):
        super().__init__(LOTTERY_DICT, db, Draw)
        
        self._players = Players(db)
        self._winners = Winners(db)
        self._config = VarDB(CONFIG_VAR, db, str)
        self._open_draw = VarDB(OPEN_DRAW_VAR, db, str)
        
        self._tickets = Tickets(db, self.open_draw.number)

    def pick(self, block:Block) -> Winner:
        try:
            open_draw = self.open_draw
            if not self._tickets:
                raise Exception('empty ticket list.')
            ticket = open_draw.random(block, self._tickets)
            if not ticket:
                raise Exception('random ticket not found.')
            
            winner = self._winners.new()
            winner.played = ticket.value
            winner.address = ticket.address
            winner.payout = open_draw.payout
            winner.timestamp = block.timestamp
            winner.draw_number = open_draw.number
            winner.chance = ticket.value / open_draw.prize
            self._winners[open_draw.number] = winner

            player = self._players[winner.address]
            if player:
                player.total_payout += winner.payout
                self._players[player.address] = player
            
            open_draw.winner = winner.address
            open_draw.picked_block = block.height
            open_draw.ticket_count = len(self._tickets)
            if block.txhash: open_draw.txhash = block.txhash
            self[open_draw.number] = open_draw

            return winner
        except Exception as e:
            revert(f'Unable to pick winning ticket: {str(e)}')

    def open(self, block:Block):
        open_draw = Draw()
        last_draw = self.last
        config = Config(self._config.get())
        open_draw.topup = config.draw_topup
        open_draw.timestamp = block.timestamp
        open_draw.opened_block = block.height
        open_draw.payout_ratio = config.draw_payout_ratio
        open_draw.number = 1000 if not last_draw else last_draw.number + 1
        self._open_draw.set(str(open_draw))
        return open_draw