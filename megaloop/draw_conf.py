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
from .consts import *
from .json_base import *

"""
Draw configuration class
"""
class DrawConf(JsonBase):
    
    def save_to(self, db:IconScoreDatabase):
        VarDB(DRAW_CONF_VAR, db, str).set(str(self))

    def __init__(self, db:IconScoreDatabase):
        self.promo = 0
        self.interval = 0
        self.payout_ratio = 0
        super().__init__(VarDB(DRAW_CONF_VAR, db, str).get())