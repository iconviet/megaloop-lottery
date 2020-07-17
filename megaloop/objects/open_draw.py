# pylint: disable=W0614
from .draw import *
from .consts import *

class OpenDraw(Draw):
    
    def save(self, db:IconScoreDatabase):
        VarDB(OPEN_DRAW_VAR, db, str).set(str(self))
    
    def __init__(self, db:IconScoreDatabase=None):
        if not db:
            super().__init__()
        else:
            super().__init__(VarDB(OPEN_DRAW_VAR, db, str).get())