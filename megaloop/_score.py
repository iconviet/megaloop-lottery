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
from ._install import *
from ._migrate import *

"""
Megaloop main SCORE composite
    * TODO: huge kludge - to refactor later
"""
class Score(Install, Migrate):

    @external(readonly=True)
    def get_config(self) -> str:
        return self._config.get()
    
    @external(readonly=True)
    def get_open_draw(self) -> str:
        draw = self._lottery.draw
        return None if not draw else str(draw)
        
    @external(readonly=True)
    def get_last_draw(self) -> str:
        draw = self._lottery.last
        return None if not draw else str(draw)

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        ticket = self._tickets.last
        return None if not ticket else str(ticket)

    @external(readonly=True)
    def get_last_player(self) -> str:
        player = self._players.last
        return None if not player else str(player)
    
    @external(readonly=True)
    def get_last_winner(self) -> str:
        winner = self._winners.last
        return None if not winner else str(winner)

    @external(readonly=True)
    def get_draw_history(self) -> str:
        return [str(draw) for draw in self._lottery]

    @external(readonly=True)
    def get_ticket_history(self, number:int) -> str:
        tickets = Tickets(self._db, number)
        return [str(ticket) for ticket in tickets]

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
    
    #######################################################

    def on_update(self):
        super().on_update()

        # self.next()

    @external
    def next(self):
        try:
            draw = self._lottery.draw
            balance = self.icx.get_balance(self.address)
            if balance < draw.payout:
                raise Exception('not enough ICX balance.')
            ##############################################
            winner = self._lottery.pick(self._block)
            address = Address.from_string(winner.address)
            self.icx.transfer(address, int(winner.payout))
            self._lottery.open()
            ##############################################
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
            self._sponsors.save(sponsor)
            return
        #####################################
        if value:
            try:
                draw = self._lottery.draw
                if draw:
                    ############################################
                    draw.prize += value
                    self._lottery.draw = draw
                    ############################################
                    player = self._players[address]
                    if player:
                        player.total_played += value
                    else:
                        player = self._players.create()
                        player.total_played = value
                        player.block = self._block.height
                        player.timestamp = self._block.timestamp
                        player.address = str(address)
                    self._players.save(player)
                    ############################################
                    ticket = self._tickets[address]
                    if ticket:
                        ticket.value += value
                        ticket.block = self._block.height
                        ticket.timestamp = self._block.timestamp
                    else:
                        ticket = self._tickets.create()
                        ticket.value = value
                        ticket.block = self._block.height
                        ticket.timestamp = self._block.timestamp
                        ticket.address = str(address)
                    self._tickets.save(ticket)
                    ############################################
                else:
                    self.icx.transfer(self.msg.sender, self.msg.value)
            except Exception as e:
                revert(f'Unable to process your transaction: {str(e)}')