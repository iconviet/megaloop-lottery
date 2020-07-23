# pylint: disable=W0614
from iconservice import *
from .objects.draws import *
from .objects.instant import *
from .objects.tickets import *
from .objects.players import *
from .objects.winners import *
from .objects.sponsors import *
from .objects.draw_conf import *
from .objects.open_draw import *

def loop(icx:float): return int(icx * 10 ** 18)
def icx(loop:int): return float(loop / 10 ** 18)
def percent(factor:int): return float(factor / 100)

class MegaloopBase(IconScoreBase):
    
    def on_update(self):
        super().on_update()

    def on_install(self):
        super().on_install()

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)

        self._db = db # later
        self._draws = Draws(db)
        self._players = Players(db)
        self._winners = Winners(db)
        self._sponsors = Sponsors(db)
        self._draw_conf = DrawConf(db)
        self._open_draw = OpenDraw(db)
        draw_number = self._open_draw.number
        self._tickets = Tickets(db, draw_number)