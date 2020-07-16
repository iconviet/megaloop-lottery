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

class MegaloopWrite(MegaloopBase):

    @external
    def withdraw(self, address:Address, amount:str):
        try:
            if self.msg.sender == self.owner:
                balance = self.icx.get_balance(self.address)
                if balance < loop(float(amount)):
                    raise Exception('not enough ICX balance')
                self.icx.transfer(address, loop(float(amount)))
        except Exception as e:
            revert(f'Unable to withdraw contract fund:{str(e)}')
    
    @external
    def next_draw(self):
        try:
            db = self._db
            instant = self._it
            open_draw = self._open_draw
            if not self._tickets:
                open_draw.block = instant.block
                open_draw.timestamp = instant.timestamp
                open_draw.save(db)
            else:
                ###############################d####################
                balance = self.icx.get_balance(self.address)
                if balance < loop(open_draw.payout):
                    raise Exception('not enough ICX balance')
                ###################################################
                winner = self.pick_winner()
                if winner:
                    address = Address.from_string(winner.address)
                    self.icx.transfer(address, int(loop(winner.payout)))
                    self._draws.save(self._open_draw)
                    self.open_draw()
                else:
                    raise Exception('winner or ticket not found')
                ###################################################
        except Exception as e:
            revert(f'Unable to proceed the next draw : {str(e)}')