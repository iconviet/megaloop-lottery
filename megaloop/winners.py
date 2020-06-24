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
from .winner import *
from iconservice import *
from .scorelib.iterable_dict import *

class Winners(IterableDictDB):
    
    def __iter__(self):
        for value in self.values():
            yield value

    def add(self, winner:Winner):
        self[winner.address] = winner.to_json()

    def update(self, winner:Winner):
        self[winner.address] = winner.to_json()

    def get_last(self) -> Winner:
        if not self: return None
        return Winner(super().get(len(self) - 1))
    
    def get(self, address:str) -> Winner:
        json = self[address]
        return None if not json else Winner(json)

    def __init__(self, db:IconScoreDatabase):
        super().__init__('winners', db, value_type=str, order=True)
