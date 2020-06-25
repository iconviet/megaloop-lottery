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
from .tickets import *
from .jsonbase import *

class Draw(JsonBase):
    
    def __init__(self, json:str=None):
        if json:
            super().__init__(json)
        else:
            # schema
            self.topup = None
            self.prize = None
            self.number = None
            self.bh_opened = None
            self.bh_closed = None
            self.tx_opened = None
            self.tx_closed = None
            self.pay_ratio = None
    
    @property
    def total_prize(self):
        return self.prize + self.topup
    
    @property
    def total_prize_pay(self):
        return self.total_prize * self.pay_ratio

    def get_winning_ticket(self, score:IconScoreBase, tickets:Tickets):
        chances = [Ticket(ticket).total / self.prize for ticket in tickets]
        seed = str(score.now() +str(self.prize) + str(len(tickets)) + str(bytes.hex(score.tx.hash)))
        distance = sum(chances) * int.from_bytes(sha3_256(seed.encode()), 'big') % 100000 / 100000.0
        for i, w in enumerate(chances):
            distance -= w
            if distance < 0:
                return tickets.get(i)
        return None
