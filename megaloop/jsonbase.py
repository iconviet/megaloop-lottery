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

class JsonBase(object):
    def __str__(self): 
        return json_dumps(self.__dict__)

    def to_json(self) -> str:
        return json_dumps(self.__dict__)

    def __init__(self, json:str=None):
        if not json:
            self.version = None
        else:
            self.__dict__ = json_loads(json)