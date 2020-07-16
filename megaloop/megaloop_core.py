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
from iconservice import *
from .objects.draws import *
from .objects.instant import *
from .objects.tickets import *
from .objects.players import *
from .objects.winners import *
from .objects.sponsors import *
from .objects.draw_conf import *
from .objects.open_draw import *

def loop(icx:float): return int(icx * 10 ** 18)
def icx(loop:int): return float(loop / 10 ** 18)
def percent(factor:int): return float(factor / 100)

class MegaloopCore(IconScoreBase):
    
    @property
    def _it(self):
        return Instant(self)
            
    def __init__(self, db: IconScoreDatabase):
        self._db = db
        super().__init__(db)
        self._draws = Draws(db)
        self._players = Players(db)
        self._winners = Winners(db)
        self._sponsors = Sponsors(db)
        self._draw_conf = DrawConf(db)
        self._open_draw = OpenDraw(db)
        draw_number = self._open_draw.number
        self._tickets = Tickets(db, draw_number)

    def pick_winner(self):
        db = self._db
        instant = self._it
        players = self._players
        winners = self._winners
        open_draw = self._open_draw
        ticket = self.__random_ticket()

        winner = winners.create()
        winner.played = ticket.amount
        winner.address = ticket.address
        winner.payout = open_draw.payout
        winner.timestamp = instant.timestamp
        winner.draw_number = str(open_draw.number)
        winner.chance = ticket.amount / open_draw.prize
        winners.save(winner)
        
        player = players[winner.address]
        player.total_payout += winner.payout
        players.save(player)

        open_draw.winner = winner.address
        open_draw.save(db)

        return winner

    def open_draw(self):
        db = self._db
        instant = self._it
        draws = self._draws
        open_draw = OpenDraw()
        last_draw = draws.get_last()
        open_draw.block = instant.block
        open_draw.timestamp = instant.timestamp
        open_draw.fill(VarDB(DRAW_CONF_VAR, db, str).get())
        open_draw.number = str(1000 if not last_draw else int(last_draw.number) + 1)
        open_draw.save(db)
        self._open_draw = open_draw

    def __random_ticket(self):
        instant = self._it
        tickets = self._tickets
        open_draw = self._open_draw
        chances = [ticket.amount / open_draw.prize for ticket in tickets]
        seed = f'{str(instant)}_{str(open_draw.prize)}_{str(len(tickets))}'
        random = (int.from_bytes(sha3_256(seed.encode()), 'big') % 100000) / 100000.0
        factor = sum(chances) * random
        for index, chance in enumerate(chances):
            factor -= chance
            if factor < 0: return tickets.get(index)
        return None