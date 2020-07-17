# pylint: disable=W0614
from iconservice import *

class Instant(object):
     
   @property
   def block(self):
      return self._block

   @property
   def txhash(self):
      return self._txhash

   @property
   def timestamp(self):
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