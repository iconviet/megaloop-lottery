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
from .draws import *
from .instant import *
from .tickets import *
from .players import *
from .winners import *
from .sponsors import *
from .draw_conf import *
from .open_draw import *
from iconservice import *

def to_loop(icx:int) -> int: return icx * 10 ** 18
def to_icx(loop:int) -> float: return loop / 10 ** 18
def to_percent(value:int) -> float: return value / 100

"""
Base class for main SCORE
"""
class MegaloopBase(IconScoreBase):
    
    @property
    def __it(self) -> Instant:
        return Instant(self)
            
    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        self._draws = Draws(db)
        self._tickets = Tickets(db)
        self._players = Players(db)
        self._winners = Winners(db)
        self._sponsors = Sponsors(db)
        self._draw_conf = DrawConf(db)
        self._open_draw = OpenDraw(db)