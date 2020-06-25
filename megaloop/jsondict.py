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
from .jsonbase import *
from iconservice import *
from .scorelib.iterable_dict import *

class JsonDictDB(IterableDictDB):
    
    def create(self) -> type:
        instance = self._type()
        instance.version = 1
        return instance

    def __iter__(self):
        for value in self.values():
            yield self._type(value)
    
    def __setitem__(self, key, value):
        super().__setitem__(key, str(value))

    def get(self, index:int) -> str:
        return self._values[self._keys[index]]
    
    def get_last(self) -> type:
        if not self: return None
        return self._type(self.get(len(self) - 1))
    
    def __getitem__(self, key) -> type:
        json = super().__getitem__(key)
        return None if not json else self._type(json)
    
    def __init__(self, key: str, db: IconScoreDatabase, type:type):
        self._type = type
        super().__init__(key, db, str, True)
    