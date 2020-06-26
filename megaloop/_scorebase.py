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
from .lottery import *
from .players import *
from .winners import *
from .toppers import *
from iconservice import *

def to_loop(icx:int) -> int: return icx * 10 ** 18
def to_icx(loop:int) -> float: return loop / 10 ** 18
def to_percent(value:int) -> float: return value / 100

class ScoreBase(IconScoreBase):
    
    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v2.0.0'

    @property
    def _moment(self) -> Moment:
        return Moment(self)
            
    def __init__(self, db: IconScoreDatabase):
        self._db = db
        super().__init__(db)
        self._lottery = Lottery(db)
        self._players = Players(db)
        self._winners = Winners(db)
        self._toppers = Toppers(db)
        self._config = VarDB(CONFIG_VAR, db, str)
        if not self._lottery.draw:
            self._tickets = Tickets(db, 0)
        else:
            self._tickets = Tickets(db, self._lottery.draw.number)