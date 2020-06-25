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
from .jsondict import *

class DrawBox(JsonDictDB):
    
    def get_open(self):
        json = self._open_draw.get()
        if not json:
            return None
        return Draw(json)
    
    def update_open(self, this:Draw):
        draw = self.get_open()
        if (draw and draw.number == this.number):
            self[draw.number] = this
        else:
            raise Exception('Open draw number mismatched')

    def open(self, bh:int, topup:int):
        if bh:
            draw = self.get_open()
            last = self.get_last()
            if not draw:
                draw = Draw()
                draw.topup = topup
                draw.bh_opened = bh
                draw.number = 1 if not last else last.number + 1
                self._open_draw.set(str(draw))
                return draw
            raise Exception('Draw is already opened')
        raise Exception('Opened block height required')
    
    def close(self, bh:int, prize:int):
        if bh:
            draw = self.get_open()
            if draw:
                draw.bh_closed = bh
                self[draw.number] = draw
                self._open_draw.remove()
                return
            else:
                raise Exception('Draw is not yet opened')
        raise Exception('Closed block height and prize required')

    def __init__(self, db:IconScoreDatabase):
        super().__init__(DRAWBOX_DICT, db, Draw)
        self._open_draw = VarDB(OPENDRAW_VAR, db, value_type=str)