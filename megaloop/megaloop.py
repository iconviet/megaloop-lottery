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
from .megaloop_task import *
from .megaloop_read import *
from .megaloop_write import *

class Megaloop(MegaloopTask, MegaloopRead, MegaloopWrite):

    @payable
    def fallback(self):
        try:
            db = self._db
            instant = self._it
            tickets = self._tickets
            players = self._players
            sponsors = self._sponsors
            open_draw = self._open_draw
            value = icx(self.msg.value)
            address = str(self.msg.sender)
            if value:
                ##############################################
                if address in sponsors:
                    sponsor = sponsors[address]
                    sponsor.total_promo += value
                    sponsors.save(sponsor)
                    return
                ##############################################
                player = players[address]
                if player:
                    player.total_played += value
                else:
                    player = players.create()
                    player.total_played = value
                    player.address = str(address)
                player.timestamp = instant.timestamp
                players.save(player)
                ##############################################
                ticket = tickets[address]
                if ticket:
                    ticket.amount += value
                else:
                    ticket = tickets.create()
                    ticket.amount = value
                    ticket.address = str(address)
                    ticket.draw_number = str(open_draw.number)
                ticket.timestamp = instant.timestamp
                if address in tickets:
                    del tickets[address]
                tickets.save(ticket)
                ##############################################
                open_draw.prize += value
                open_draw.ticket_count = len(tickets)
                open_draw.save(db)
                ##############################################
        except Exception as e:
            revert(f'Unable to process transaction: {str(e)}')