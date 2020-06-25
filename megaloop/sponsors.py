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
from .sponsor import *
from .dictbase import *

class Sponsors(DictBase):
    
    def create(self) -> Sponsor:
        sponsor = Sponsor()
        sponsor.version = 1
        return sponsor

    def add_or_update(self, sponsor:Sponsor):
        self[str(sponsor.address)] = sponsor

    def get_last(self) -> Sponsor:
        if not self: return None
        return Sponsor(super().get(len(self) - 1))
    
    def __getitem__(self, key) -> Sponsor:
        json = super().__getitem__(str(key))
        return None if not json else Sponsor(json)

    def __init__(self, db:IconScoreDatabase):
        super().__init__(SPONSOR_DICT, db, value_type=str)