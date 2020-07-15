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
from .megaloop_base import *

"""
SCORE internal functions
"""
class MegaloopCore(MegaloopBase):
    
    def pick(self) -> Winner:
        db = self._db
        instant = self._it
        ticket = self.rand()
        open_draw = self._open_draw

        winner = self._winners.create()
        winner.played = ticket.value
        winner.address = ticket.address
        winner.payout = open_draw.payout
        winner.timestamp = instant.timestamp
        winner.draw_number = open_draw.number
        winner.chance = ticket.value / open_draw.prize
        
        player = self._players[winner.address]
        player.total_payout += winner.payout

        self._players.save(player)
        self._winners.save(winner)

        open_draw.winner = winner.address
        open_draw.closed_block = instant.block
        open_draw.closed_timestamp = instant.block
        open_draw.ticket_count = len(self._tickets)
        if instant.txhash: open_draw.txhash = instant.txhash
        open_draw.save_to(db)

        return winner

    def open(self):
        db = self._db
        instant = self._it
        open_draw = self._open_draw
        last_draw = self._draws.get_last()
        open_draw.opened_block = instant.block
        open_draw.opened_timestamp = instant.timestamp
        open_draw.number = 1000 if not last_draw else last_draw.number + 1
        open_draw.save_to(db)

    def rand(self):
        instant = self._it
        tickets = self._tickets
        open_draw = self._open_draw
        chances = [ticket.value / open_draw.prize for ticket in tickets]
        seed = f'{str(instant)}_{str(open_draw.prize)}_{str(len(tickets))}'
        random = (int.from_bytes(sha3_256(seed.encode()), 'big') % 100000) / 100000.0
        factor = sum(chances) * random
        for index, chance in enumerate(chances):
            factor -= chance
            if factor < 0: return tickets.get(index)
        return None