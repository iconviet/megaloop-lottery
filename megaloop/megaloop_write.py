# pylint: disable=W0614
from .megaloop_base import *

class MegaloopWrite(MegaloopBase):

    @external
    def set_draw_conf(self, json:str):
        self._draw_conf.load(json)
        self._open_draw.fill(json)
        self._draw_conf.save(self._db)
        self._open_draw.save(self._db)
    
    @external
    def withdraw(self, address:Address, amount:str):
        if self.msg.sender == self.owner:
            self.icx.transfer(address, loop(float(amount)))
    
    @external
    def next_draw(self):
        try:
            db = self._db
            instant = self._it
            open_draw = self._open_draw
            if not self._tickets:
                open_draw.block = instant.block
                open_draw.timestamp = instant.timestamp
                open_draw.save(db)
            else:
                ###############################d####################
                balance = self.icx.get_balance(self.address)
                if balance < loop(open_draw.payout):
                    raise Exception('not enough ICX balance')
                ###################################################
                winner = self.pick_winner()
                if winner:
                    address = Address.from_string(winner.address)
                    self.icx.transfer(address, loop(winner.payout))
                    self._draws.save(self._open_draw)
                    self.open_draw()
                else:
                    raise Exception('winner or ticket not found')
                ###################################################
        except Exception as e:
            revert(f'Unable to proceed the next draw : {str(e)}')