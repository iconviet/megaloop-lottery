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
from iconservice import *

class Config(object):
    
    def save(self):
        self._config.set(json_dumps(self.__dict__))

    def __init__(self, db:IconScoreDatabase):
        self._config = VarDB('config', db, value_type=str)
        if not self._config.get():
            self.payout_ratio = None
        else:
            self.__dict__ = json_loads(self._config.get())
