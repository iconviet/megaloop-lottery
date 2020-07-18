# pylint: disable=W0614
from iconservice import *

class JsonBase(object):
    
    def __init__(self, text:str=None):
        if text: self.load(text)

    def __repr__(self):
        return json_dumps(self.__dict__)

    def load(self, text:str):
        if text: self.__dict__ = json_loads(text)

    def fill(self, text:str):
        if text: self.__dict__.update(json_loads(text))