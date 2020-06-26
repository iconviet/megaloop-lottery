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
from .draw import *
from .consts import *
from .config import *
from .instant import *
from .jsondict import *

class DrawBox(JsonDictDB):
    
    def get_open(self):
        json = self._open_draw.get()
        if not json:
            return None
        return Draw(json)
    
    def set_open(self, this:Draw):
        draw = self.get_open()
        if draw and draw.number == this.number:
            self._open_draw.set(str(this))
            return
        raise Exception('Open draw number mismatched')

    def open(self, config:Config, instant:Instant):
        if instant.bh:
            draw = self.get_open()
            last = self.get_last()
            if not draw:
                draw = Draw()
                draw.bh_opened = instant.bh
                draw.topping = config.draw_topping
                draw.payout_ratio = config.payout_ratio
                if instant.tx: draw.tx_opened = instant.tx
                draw.number = 1 if not last else last.number + 1
                self._open_draw.set(str(draw))
                return draw
            raise Exception('Draw already opened')
        raise Exception('Opened block required')
    
    def close(self, config:Config, instant:Instant):
        if instant.bh:
            draw = self.get_open()
            if draw:
                draw.bh_closed = instant.bh
                if instant.tx: draw.tx_closed = instant.tx
                self[draw.number] = draw
                self._open_draw.remove()
                return
            raise Exception('Draw not yet opened')
        raise Exception('Closed block required')

    def __init__(self, db:IconScoreDatabase):
        super().__init__(DRAWBOX_DICT, db, Draw)
        self._open_draw = VarDB(OPEN_DRAW_JSON, db, value_type=str)
