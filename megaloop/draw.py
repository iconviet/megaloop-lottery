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
            self.total = 0
            self.number = 0
            self.topping = 0
            self.bh_opened = 0
            self.bh_closed = 0
            self.tx_opened = None
            self.tx_closed = None
            self.tx_drawed = None
            self.payout_ratio = 0
    
    @property
    def prize(self) -> int:
        return self.total + self.topping
    
    @property
    def payout(self) -> int:
        return self.prize * self.payout_ratio

    def random(self, instant:Instant, tickets:Tickets):
        changes = [Ticket(ticket).total / self.prize for ticket in tickets]
        random_factor = f'{str(instant)}_{str(self.prize)}_{str(len(tickets))}'
        remaining_distance = sum(changes) * int.from_bytes(sha3_256(random_factor.encode()), 'big') % 100000 / 100000.0
        for i, w in enumerate(changes):
            remaining_distance -= w
            if remaining_distance < 0:
                return tickets.get(i)
        return None
