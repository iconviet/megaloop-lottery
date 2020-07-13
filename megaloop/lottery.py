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
    def draw(self) -> Draw:
        json = self._draw.get()
        if not json:
            return None
        return Draw(json)
    
    @draw.setter
    def draw(self, this:Draw):
        draw = self.draw
        if draw and draw.number == this.number:
            self._draw.set(str(this))
            return
        raise Exception('draw number mismatch')

    def open(self, block:Block):
        draw = Draw()
        last = self.last
        if not last:
            draw.number = 1
        else:
            draw.number = last.number + 1
        config = Config(self._config.get())
        draw.topup = config.payout_topup
        draw.opened_block = block.height
        draw.payout_ratio = config.payout_ratio
        self._draw.set(str(draw))
        return draw
    
    def __init__(self, db:IconScoreDatabase):
        self._players = Players(db)
        self._winners = Winners(db)
        self._draw = VarDB(DRAW_VAR, db, str)
        super().__init__(LOTTERY_DICT, db, Draw)
        self._config = VarDB(CONFIG_VAR, db, str)
        if not self.draw:
            self._tickets = Tickets(db, 0)
        else:
            self._tickets = Tickets(db, self.draw.number)

    def pick(self, block:Block) -> Winner:
        try:
            draw = self.draw
            if not draw:
                raise Exception('draw not opened.')
            if not self._tickets:
                raise Exception('empty ticket list.')
            ticket = draw.random(block, self._tickets)
            if not ticket:
                raise Exception('random ticket not found.')
            
            winner = self._winners.new()
            winner.payout = draw.payout
            winner.played = ticket.value
            winner.address = ticket.address
            winner.draw_number = draw.number
            winner.timestamp = block.timestamp
            winner.chance = ticket.value / draw.prize
            self._winners[draw.number] = winner

            player = self._players[winner.address]
            if player:
                player.total_payout += winner.payout
                self._players[player.address] = player
            
            draw.winner = winner.address
            draw.drawed_block = block.height
            draw.ticket_count = len(self._tickets)
            if block.txhash: draw.txhash = block.txhash
            self[draw.number] = draw
            
            return winner
        except Exception as e:
            revert(f'Unable to pick winning ticket: {str(e)}')