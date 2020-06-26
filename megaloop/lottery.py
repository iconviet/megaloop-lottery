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
from .consts import *
from .config import *
from .moment import *
from .winners import *
from .jsondict import *
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

    def open(self):
        draw = self.draw
        if not draw:
            draw = Draw()
            last = self.last
            if not last:
                draw.number = 1
            else:
                draw.number = last.number + 1
            config = Config(self._config.get())
            draw.topping = config.draw_topping
            draw.payout_ratio = config.payout_ratio
            self._draw.set(str(draw))
            return draw
    
    def pick(self, moment:Moment) -> Winner:
        if not self._tickets:
            raise Exception('empty ticket list.')
        draw = self.draw
        if not draw:
            raise Exception('draw not yet opened.')
        ticket = draw.random(moment, self._tickets)
        if not ticket:
            raise Exception('random ticket not found.')
        
        winner = self._winners.create()
        winner.bh = moment.bh
        winner.payout = draw.payout
        winner.address = ticket.address
        self._winners.save(winner)
        
        draw.bh = moment.bh
        draw.winner = winner.address
        if moment.tx: draw.tx = moment.tx
        self[draw.number] = draw
        self._draw.remove()
        
        return winner

    def __init__(self, db:IconScoreDatabase):
        self._players = Winners(db)
        self._winners = Winners(db)
        self._draw = VarDB(DRAW_VAR, db, str)
        super().__init__(LOTTERY_DICT, db, Draw)
        self._config = VarDB(CONFIG_VAR, db, str)
        if self.draw:
            self._tickets = Tickets(db, self.draw.number)
        