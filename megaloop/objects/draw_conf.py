# pylint: disable=W0614
from .consts import *
from .json_base import *

class DrawConf(JsonBase):
    
    def save(self, db:IconScoreDatabase):
        VarDB(DRAW_CONF_VAR, db, str).set(str(self))

    def __init__(self, db:IconScoreDatabase=None):
        if not db:
            self.promo = 0
            self.block_count = 0
            self.payout_ratio = 0
            self.seeding_limit = 0
            self.revenue_limit = 0
        else:
            super().__init__(VarDB(DRAW_CONF_VAR, db, str).get())