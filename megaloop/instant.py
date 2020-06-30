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

"""
Point in time snapshot/representation
"""
class Instant(object):
     
   @property
   def now(self) -> int:
      return self._now

   @property
   def block(self) -> int:
      return self._block

   @property
   def txhash(self) -> str:
      return self._txhash
   
   def __repr__(self):
      s = f'{self.now}_{self._block}'
      return s if not self._txhash else f'{s}_{self.txhash}'

   def __init__(self, icon:IconScoreBase):
      self._now = icon.now()
      self._block = icon.block_height
      self._txhash = None if not icon.tx else f'0x{bytes.hex(icon.tx.hash)}'
