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
from .json_base import *

class Draw(JsonBase):
    
    def __init__(self, json:str=None):
        self.prize = 0 
        self.promo = 0       
        self.number = 0
        self.txhash = None
        self.winner = None
        self.block_count = 0
        self.ticket_count = 0
        self.payout_ratio = 0
        self.opened_block = 0
        self.closed_block = 0
        self.opened_timestamp = 0
        self.closed_timestamp = 0
        super().__init__(json)
    
    @property
    def total(self) -> int:
        return self.prize + self.promo

    @property
    def payout(self) -> int:
        return int(self.total * self.payout_ratio)