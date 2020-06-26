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

class Score(Install, Migrate):

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
    def get_draw_history(self) -> str:
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

    ####################################################

    def on_update(self):
        super().on_update()

        self.draw()

    @external
    def open(self):
        self._drawbox.open(Config(self._config.get()), self._instant)
    
    @external
    def draw(self):
        try:
            if not self._tickets:
                raise Exception('empty ticket list.')
            
            draw = self._drawbox.get_open()
            if not draw:
                raise Exception('draw not yet opened.')
            
            balance = self.icx.get_balance(self.address)
            if balance < draw.payout:
                raise Exception('not enough ICX to send.')
            
            ticket = draw.randomize(self._tickets, self._instant)
            if not ticket:
                raise Exception('randomized draw ticket not found.')

            ########################################################################
            
            winner = self._winners.create()
            winner.payout = draw.payout
            winner.bh = self._instant.bh
            winner.address = ticket.address
            winner.name = self._players[ticket.address].name
            self._winners.save(winner)
            
            self._drawbox.close(winner, self._instant)
            
            self.icx.transfer(Address.from_string(winner.address), int(draw.payout))
            
            self._drawbox.open(Config(self._config.get()), self._instant)
            ########################################################################

        except Exception as e:
            revert(f'Unable to draw winning ticket: {str(e)}')

    @payable
    def fallback(self):
        value = self.msg.value
        address = str(self.msg.sender)
        ###################################
        if address in self._toppers:
            topper = self._toppers[address]
            topper.total += value
            self._toppers.save(topper)
            return
        ###################################
        if value:
            try:
                draw = self._drawbox.get_open()
                if draw:
                    ##################################
                    draw.total += value
                    self._drawbox.set_open(draw)
                    ##################################
                    player = self._players[address]
                    if player:
                        player.total += value
                    else:
                        player =self._players.create()
                        player.total = value
                        player.bh = self._instant.bh
                        player.address = str(address)
                    self._players.save(player)
                    ##################################
                    ticket = self._tickets[address]
                    if ticket:
                        ticket.total += value
                        ticket.bh = self._instant.bh
                    else:
                        ticket = self._tickets.create()
                        ticket.total = value
                        ticket.bh = self._instant.bh
                        ticket.address = str(address)
                    self._tickets.save(ticket)
                    ##################################
                else:
                    self.icx.transfer(self.msg.sender, self.msg.value)
            except Exception as e:
                revert(f'Unable to process your transaction: {str(e)}')