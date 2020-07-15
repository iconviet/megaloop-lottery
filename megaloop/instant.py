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
Instant information
"""
class Instant(object):
     
   @property
   def block(self) -> int:
      return self._block

   @property
   def txhash(self) -> str:
      return self._txhash

   @property
   def timestamp(self) -> int:
      return self._timestamp
   
   def __repr__(self):
      if not self.txhash:
         return f'{self.block}_{self.timestamp}'
      else:
         return f'{self.block}_{self.timestamp}_{self.txhash}'

   def __init__(self, base:IconScoreBase):
      self._timestamp = base.now()
      self._block = base.block_height
      self._txhash = None if not base.tx else f'0x{bytes.hex(base.tx.hash)}'