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
from .megaloop_base import *

class MegaloopTask(MegaloopBase):

    def on_update(self):
        super().on_update()

    def on_install(self):
        super().on_install()
        
        draw_conf = self._draw_conf
        draw_conf.promo = 1.2345
        draw_conf.block_count = 150
        draw_conf.payout_ratio = percent(100)
        draw_conf.save(self._db)
        
        sponsor = self._sponsors.create()
        sponsor.address = str(self.owner)
        self._sponsors.save(sponsor)
        
        self.open_draw()