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

JSON_VERSION = 1

CONFIG_JSON = 'config'
DRAWBOX_DICT = 'drawbox'
TICKETS_DICT = 'tickets'
PLAYERS_DICT = 'players'
WINNERS_DICT = 'winners'
TOPPERS_DICT = 'toppers'
OPEN_DRAW_JSON = 'open_draw'

def to_loop(coin:int) -> int: return coin * 10**18

def to_coin(loop:int) -> float: return loop / 10**18

def to_percent(value:int) -> float: return value / 100