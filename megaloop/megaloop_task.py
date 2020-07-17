# pylint: disable=W0614
from .megaloop_base import *

class MegaloopTask(MegaloopBase):

    def on_update(self):
        super().on_update()

    def on_install(self):
        super().on_install()
        
        draw_conf = self._draw_conf
        draw_conf.promo = 1.2345
        draw_conf.block_count = 150
        draw_conf.payout_ratio = percent(100)
        draw_conf.save(self._db)
        
        sponsor = self._sponsors.create()
        sponsor.address = str(self.owner)
        self._sponsors.save(sponsor)
        
        self.open_draw()