# pylint: disable=W0614
from iconservice import *

class JsonBase(object):
    
    def __init__(self, json:str=None):
        if json: self.load(json)

    def __repr__(self):
        return json_dumps(self.__dict__)

    def load(self, json:str):
        if json: self.__dict__ = json_loads(json)

    def fill(self, json:str):
        if json: self.__dict__.update(json_loads(json))