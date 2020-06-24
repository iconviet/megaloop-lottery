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
from .config import *
from .ticket import *
from .player import *
from .winner import *
from .ranking import *
from .tickets import *
from .players import *
from iconservice import *
from .scorelib.set import *
from .scorelib.iterable_dict import *

class Megaloop(IconScoreBase):
        
    def on_update(self):
        super().on_update()
    
    def on_install(self):
        super().on_install()
        
        self._reserve_ratio.set(15)
        self._sponsors.add(self.owner)
        self._draw_id.set(self.block_height)
        self._sequences.add(self.block_height)
        self._seeding_limit.set(5 * 10 ** 18)
        self._prize_limit.set(1000 * 10 ** 18)

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        
        self.config = Config(db)
        self._tickets = Tickets(db)
        self._players = Players(db)
        
        self._draw_id = VarDB('draw_id', db, value_type=int)
        self._draw_prize = VarDB('draw_prize', db, value_type=int)
        self._prize_limit = VarDB('prize_limit', db, value_type=int)
        self._last_draw_id = VarDB('last_draw_id', db, value_type=int)
        self._last_draw_bh = VarDB('last_draw_bh', db, value_type=int)
        self._last_draw_tx = VarDB('last_draw_tx', db, value_type=str)
        self._seeding_limit = VarDB('seeding_limit', db, value_type=int)
        self._reserve_ratio = VarDB('reserve_ratio', db, value_type=int)
        
        self._treasury_addr = VarDB('treasury_addr', db, value_type=Address)
        
        self._sequences = SetDB('sequences', db, value_type=int, order=True)
        self._sponsors = SetDB('sponsors', db, value_type=Address, order=True)

        self._winners = IterableDictDB('winners', db, value_type=str, order=True)
        self._ranking = IterableDictDB('ranking', db, value_type=str, order=True)
        
    ####################################################################################################

    @payable
    def fallback(self):
        value = self.msg.value
        address = self.msg.sender
        if address in self._sponsors:
            return
        if value == 0:
            revert('Zero value is not allowed')
        # if not self.config.enabled:
        #     revert('Contract is currently disabled')
        if self._last_draw_bh.get() == self.block_height:
            revert('Draw in progress. Deposit is not allowed')
        try:
            ticket = self._tickets.get(str(address))
            player = self._players.get(str(address))
            if not ticket:
                # create ticket
                ticket = Ticket()
                ticket.version = 1
                ticket.value = value
                ticket.address = str(address)
                ticket.block = self.block_height
                self._tickets.add(ticket)
            else:
                # replace ticket
                ticket.block = self.block_height
                ticket.value = ticket.value + value
                self._tickets.update(ticket)
            if not player:
                # create player
                player = Player()
                player.version = 1
                player.value = value
                player.address = str(address)
                player.block = self.block_height
                self._players.add(player)
            else:
                # update player
                player.value = player.value + value
                self._players.update(player)
            self._draw_prize.set(self._draw_prize.get() + value)
        except Exception as e:
            revert(f'Megaloop was unable to process your transaction. Error: {str(e)}')
    
    ####################################################################################################

    @external
    def set_enabled(self, enabled: bool):
        if self.msg.sender == self.owner:
            self.config.enabled = enabled
            self.config.save()

    @external
    def add_sponsor(self, address: Address):
        if address not in self._sponsors:
            self._sponsors.add(address)

    @external
    def set_prize_limit(self, prize_limit: int):
        if self.msg.sender == self.owner:
            self._prize_limit.set(prize_limit)
    
    @external
    def set_reserve_ratio(self, reserve_ratio: int):
        if self.msg.sender == self.owner:
            self._reserve_ratio.set(reserve_ratio)
    
    @external
    def set_seeding_limit(self, seeding_limit: int):
        if self.msg.sender == self.owner:
            self._seeding_limit.set(seeding_limit)

    @external
    def set_treasury_address(self, address: Address):
        if self.msg.sender == self.owner:
            self._treasury_addr.set(address)

    ####################################################################################################
    
    def _calculate(self, chances: list) -> int:
        remaining_distance = self._randomize() * sum(chances)
        for i, w in enumerate(chances):
            remaining_distance -= w
            if remaining_distance < 0:
                return i

    def _randomize(self) -> float:
        seed = str(self.now() +
               str(len(self._tickets)) +
               str(self._draw_prize.get()) +
               str(bytes.hex(self.tx.hash)))
        return int.from_bytes(sha3_256(seed.encode()), 'big') % 100000 / 100000.0

    @external
    def draw_winning_ticket(self):
        if len(self._tickets) > 0:
            """
            1. caculate required values
            """
            draw_prize = self._draw_prize.get()
            prize_limit = self._prize_limit.get()
            seeding_limit = self._seeding_limit.get()
            reserve_ratio = self._reserve_ratio.get()
            reserve_value = draw_prize * reserve_ratio  // 100
            real_prize = draw_prize * (100 - reserve_ratio) // 100
            draw_seeding = prize_limit - real_prize if real_prize < prize_limit else 0
            real_prize = real_prize + (draw_seeding if draw_seeding < seeding_limit else seeding_limit)            
            """
            2. check for sufficient fund
            """
            icx_minimum = real_prize + reserve_value
            icx_balance = self.icx.get_balance(self.address)
            if icx_balance < icx_minimum:
                revert(f'Insufficient fund. {icx_minimum/10**18} ICX is required')
            """
            3. start calculating winning ticket chances
            """
            chances = [Ticket(ticket).value / draw_prize for ticket in self._tickets]
            index = self._calculate(chances)
            try:
                """
                4. transfer real prize to winner's address
                """
                address = self._tickets.get[index]
                self.icx.transfer(address, real_prize)
                """
                5. transfer reserve value to treasury address
                """
                treasury_addr = self._treasury_addr.get()
                if treasury_addr is not None and reserve_value > 0:
                    self.icx.transfer(treasury_addr, reserve_value)
                """
                6. record winning address, real prize, block height
                """
                winner = Winner()
                winner.version = 1
                winner.prize = real_prize
                winner.block = self.block_height
                self._winners[address] = str(winner)
                """
                7. record last draw information and start next draw
                """
                self._draw_prize.set(0)
                self._draw_id.set(self.block_height)
                self._sequences.add(self.block_height)
                self._last_draw_bh.set(self.block_height)
                self._last_draw_tx.set(f'0x{bytes.hex(self.tx.hash)}')
            except Exception as e:
                revert(f'Failed to process transaction. Error: {str(e)}')

    ####################################################################################################

    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v1.1.0'

    @external(readonly=True)
    def get_enabled(self) -> bool:
        return self.config.enabled

    @external(readonly=True)
    def get_draw_id(self) -> int:
        return self._draw_id.get()

    @external(readonly=True)
    def get_draw_prize(self) -> int:
        return self._draw_prize.get()

    @external(readonly=True)
    def get_prize_limit(self) -> int:
        return self._prize_limit.get()

    @external(readonly=True)
    def get_last_draw_bh(self) -> int:
        return self._last_draw_bh.get()
    
    @external(readonly=True)
    def get_seeding_limit(self) -> int:
        return self._seeding_limit.get()
    
    @external(readonly=True)
    def get_reserve_ratio(self) -> int:
        return self._reserve_ratio.get()

    @external(readonly=True)
    def get_last_ticket(self) -> str:
        return str(self._tickets.get_last())

    @external(readonly=True)
    def get_last_player(self) -> str:
        return str(self._players.get_last())

    @external(readonly=True)
    def get_treasury_address(self) -> Address:
        return self._treasury_addr.get()
    
    @external(readonly=True)
    def get_sequences(self) -> list:
        return [str(x) for x in self._sequences]
    
    @external(readonly=True)
    def get_sponsors(self) -> list:
        return [str(x) for x in self._sponsors]
    
    @external(readonly=True)
    def get_last_winner(self) -> str:
        if not self._winners:
            return None
        return self._winners[len(self._winners) - 1]

    @external(readonly=True)
    def get_tickets(self) -> str:
        return [ticket for ticket in self._tickets]

    @external(readonly=True)
    def get_players(self) -> str:
        return [player for player in self._players]

    @external(readonly=True)
    def get_winners(self) -> str:
        return [winner for winner in self._winners]

    @external(readonly=True)
    def get_ranking(self) -> str:
        return [player for player in self._ranking.values()]
        
    @external(readonly=True)
    def get_draw_seeding(self) -> int:
        draw_prize = self._draw_prize.get()
        prize_limit = self._prize_limit.get()
        seeding_limit = self._seeding_limit.get()
        reserve_ratio = self._reserve_ratio.get()
        real_prize = (100 - reserve_ratio) * draw_prize // 100
        draw_seeding = prize_limit - real_prize if real_prize < prize_limit else 0
        draw_seeding = draw_seeding if draw_seeding < seeding_limit else seeding_limit
        return draw_seeding