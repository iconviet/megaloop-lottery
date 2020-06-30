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
from .instant import *
from .tickets import *
from .jsonbase import *

class Draw(JsonBase):
    
    def __init__(self, json:str=None):
        if json:
            super().__init__(json)
        else:
            # schema                        
            self.prize = 0
            self.topup = 0
            self.block = 0
            self.number = 0
            self.txhash = None
            self.winner = None
            self.payout_ratio = 0
    
    @property
    def total(self) -> int:
        return self.prize + self.topup
    
    @property
    def payout(self) -> int:
        return int(self.total * self.payout_ratio)

    def random(self, instant:Instant, tickets:Tickets):
        weights = [ticket.value / self.prize for ticket in tickets]
        seed = f'{str(instant)}_{str(self.prize)}_{str(len(tickets))}'
        random = (int.from_bytes(sha3_256(seed.encode()), 'big') % 100000) / 100000.0
        remaining_distance = sum(weights) * random
        for i, w in enumerate(weights):
            remaining_distance -= w
            if remaining_distance < 0:
                return tickets.get(i)
        return None