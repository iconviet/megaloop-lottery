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
class Megaloop(Install, Migrate):

    @external(readonly=True)
    def get_config(self) -> str:
        return self._config.get()
    
    @external
    def set_config(self, json:str):
        self._config.set(json)

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        ticket = self._tickets.last
        if not ticket:
            return None
        draw = self._lottery.open_draw
        ticket.chance = ticket.value / draw.prize
        return str(ticket)

    @external(readonly=True)
    def get_last_player(self) -> str:
        player = self._players.last
        return None if not player else str(player)
    
    @external(readonly=True)
    def get_last_winner(self) -> str:
        winner = self._winners.last
        return None if not winner else str(winner)

    @external(readonly=True)
    def get_open_draw(self) -> str:
        open_draw = self._lottery.open_draw
        return None if not open_draw else str(open_draw)

    @external(readonly=True)
    def get_last_draw(self) -> str:
        last_draw = self._lottery.last
        return None if not last_draw else str(last_draw)

    @external(readonly=True)
    def get_players(self, skip:int=0, take:int=0) -> str:
        return [str(player) for player in self._players]
    
    @external(readonly=True)
    def get_sponsors(self, skip:int=0, take:int=0) -> str:
        return [str(sponsor) for sponsor in self._sponsors]
    
    @external(readonly=True)
    def get_past_draws(self, skip:int=0, take:int=0) -> str:
        return [str(draw) for draw in self._lottery]

    @external(readonly=True)
    def get_past_winners(self, skip:int=0, take:int=0) -> str:
        return [str(winner) for winner in self._winners]

    @external(readonly=True)
    def get_tickets(self, skip:int=0, take:int=0) -> str:
        def calculate_chance(ticket:Ticket):
            ticket.chance = ticket.value / self._lottery.open_draw.prize
            return ticket
        return [str(calculate_chance(ticket)) for ticket in self._tickets]
    
    @external(readonly=True)
    def get_past_tickets(self, draw_number:int, skip:int=0, take:int=0) -> str:
        tickets = Tickets(self._db, draw_number)
        return [str(ticket) for ticket in tickets]
    
    ###########################################################################

    @external
    def next_draw(self):
        try:
            open_draw = self._lottery.open_draw
            if not open_draw:
                raise Exception('draw not opened.')
            if not self._tickets:
                open_draw.timestamp = self._block.timestamp
                open_draw.opened_block = self._block.height
                self._lottery.open_draw = open_draw
            else:
                ##################################################
                balance = self.icx.get_balance(self.address)
                if balance < open_draw.payout:
                    raise Exception('not enough ICX balance.')
                ##################################################
                winner = self._lottery.pick(self._block)
                if winner:
                    address = Address.from_string(winner.address)
                    self.icx.transfer(address, int(winner.payout))
                    self._lottery.open(self._block)
                else:
                    raise Exception('winner or ticket not found.')
                ##################################################
        except Exception as e:
            revert(f'Unable to draw winning ticket: {str(e)}')

    @payable
    def fallback(self):
        value = self.msg.value
        address = str(self.msg.sender)
        #####################################
        if address in self._sponsors:
            sponsor = self._sponsors[address]
            sponsor.total_topup += value
            self._sponsors[address] = sponsor
            return
        #####################################
        if value:
            try:
                draw = self._lottery.open_draw
                if draw:
                    ########################################
                    draw.prize += value
                    ########################################
                    player = self._players[address]
                    if player:
                        player.total_played += value
                    else:
                        player = self._players.new()
                        player.total_played = value
                        player.address = str(address)
                    player.timestamp = self._block.timestamp
                    self._players[address] = player
                    ########################################
                    ticket = self._tickets[address]
                    if ticket:
                        ticket.value += value
                    else:
                        ticket = self._tickets.new()
                        ticket.value = value
                        ticket.address = str(address)
                        ticket.draw_number = draw.number
                    ticket.timestamp = self._block.timestamp
                    if address in self._tickets:
                        del self._tickets[address]
                    self._tickets[address] = ticket
                    ########################################
                    draw.ticket_count = len(self._tickets)
                    self._lottery.open_draw = draw
                    ########################################
                else:
                    self.icx.transfer(self.msg.sender, self.msg.value)
            except Exception as e:
                revert(f'Unable to process your transaction: {str(e)}')