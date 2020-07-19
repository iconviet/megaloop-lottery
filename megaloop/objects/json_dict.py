# pylint: disable=W0614
from iconservice import *
from .scorelib.iterable_dict import *

class JsonDictDB(IterableDictDB):
    
    def create(self):
        instance = self._type()
        instance.version = 1
        return instance

    def __iter__(self):
        for value in self.values():
            yield self._type(value)
    
    def __setitem__(self, key, value):
        super().__setitem__(key, str(value))

    def get_last(self):
        return self.get(-1) if self else None

    def __getitem__(self, key):
        json = super().__getitem__(key)
        return self._type(json) if json else None

    def get(self, index:int):
        return self._type(self._values[self._keys[index]])
    
    def __init__(self, key: str, db: IconScoreDatabase, type:type):
        self._type = type
        super().__init__(key, db, str, True)