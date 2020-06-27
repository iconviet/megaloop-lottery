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

class Instant(object):
     
   @property
   def tt(self) -> int:
      return self._tt

   @property
   def bh(self) -> int:
      return self._bh

   @property
   def tx(self) -> str:
      return self._tx
   
   def __repr__(self):
      s = f'{self.tt}_{self._bh}'
      return s if not self._tx else f'{s}_{self.tx}'

   def __init__(self, icon:IconScoreBase):
      self._tt = icon.now()
      self._bh = icon.block_height
      self._tx = None if not icon.tx else f'0x{bytes.hex(icon.tx.hash)}'