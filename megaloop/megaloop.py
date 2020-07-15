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
from .megaloop_install import *
from .megaloop_migrate import *

"""
Megaloop main SCORE composite
    * TODO: still kludgy - refactor later
"""
class Megaloop(MegaloopInstall, MegaloopMigrate):

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
        ticket.chance = ticket.value / open_draw.prize
        return str(ticket)

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
    def get_past_tickets(self, draw_number:int) -> str:
        return [str(ticket) for ticket in self._tickets[draw_number]]
    
    @external(readonly=True)
    def get_tickets(self) -> str:
        open_draw = self._open_draw
        def calculate_chance(ticket:Ticket):
            ticket.chance = ticket.value / open_draw.prize
            return ticket
        return [str(calculate_chance(ticket)) for ticket in self._tickets]
    
    ###########################################################################

    @payable
    def fallback(self):
        try:
            db = self._db
            instant = self._it
            value = self.msg.value
            tickets = self._tickets
            players = self._players
            sponsors = self._sponsors
            open_draw = self._open_draw
            address = str(self.msg.sender)
            if value:
                ###########################################
                if address in sponsors:
                    sponsor = sponsors[address]
                    sponsor.total_promo += value
                    sponsors[address] = sponsor
                    return
                ###########################################
                player = players[address]
                if player:
                    player.total_played += value
                else:
                    player = players.create()
                    player.total_played = value
                    player.address = str(address)
                player.timestamp = instant.timestamp
                players[address] = player
                ###########################################
                ticket = tickets[address]
                if ticket:
                    ticket.value += value
                else:
                    ticket = tickets.create()
                    ticket.value = value
                    ticket.address = str(address)
                    ticket.draw_number = open_draw.number
                ticket.last_block = instant.block
                ticket.timestamp = instant.timestamp
                if address in tickets:
                    del tickets[open_draw.number][address]
                tickets[open_draw.number][address] = ticket
                ###########################################
                open_draw.prize += value
                open_draw.ticket_count = len(tickets)
                open_draw.save_to(db)
                ###########################################
        except Exception as e:
            revert(f'Unable to process transaction: {str(e)}')

    @external
    def withdraw(self, address:Address, value:int):
        try:
            if self.msg.sender == self.owner:
                balance = self.icx.get_balance(self.address)
                if balance < value:
                    raise Exception('not enough ICX balance')
                self.icx.transfer(address, to_loop(int(value)))
        except Exception as e:
            revert(f'Unable to withdraw contract fund:{str(e)}')
    
    @external
    def next_draw(self):
        try:
            db = self._db
            instant = self._it
            open_draw = self._open_draw
            if not self._tickets:
                open_draw.opened_block = instant.block
                open_draw.opened_timestamp = instant.timestamp
                open_draw.save_to(db)
            else:
                #################################################
                balance = self.icx.get_balance(self.address)
                if balance < open_draw.payout:
                    raise Exception('not enough ICX balance')
                #################################################
                winner = self.pick()
                if winner:
                    address = Address.from_string(winner.address)
                    self.icx.transfer(address,int(winner.payout))
                    self.open()
                else:
                    raise Exception('winner or ticket not found')
                #################################################
        except Exception as e:
            revert(f'Unable to proceed the next draw : {str(e)}')