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
from .ticket import *
from iconservice import *
from .scorelib.iterable_dict import *

class Tickets(IterableDictDB):
    
    def __iter__(self):
        for value in self.values():
            yield value
    
    def add(self, ticket:Ticket):
        self[ticket.address] = ticket.to_json()

    def update(self, ticket:Ticket):
        self[ticket.address] = ticket.to_json()

    def get_last(self) -> Ticket:
        if not self: return None
        return Ticket(super().get(len(self) - 1))

    def get(self, address:str) -> Ticket:
        json = self[address]
        return None if not json else Ticket(json)
    
    def __init__(self, db:IconScoreDatabase):
        super().__init__('tickets', db, value_type=str, order=True)