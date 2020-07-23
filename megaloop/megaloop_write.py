# pylint: disable=W0614
from .megaloop_base import *

class MegaloopWrite(MegaloopBase):

    @property
    def _it(self):
        return Instant(self)
    
    def on_update(self):
        super().on_update()
        '''
        migration / maintenance code go here
        '''

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
        
        self.__open_draw()

    @external
    def set_draw_conf(self, text:str):
        self._draw_conf.load(text)
        self._open_draw.fill(text)
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
            it = self._it
            open_draw = self._open_draw
            if not self._tickets:
                open_draw.block = it.block
                open_draw.timestamp = it.timestamp
                open_draw.save(db)
            else:
                ###############################d####################
                balance = self.icx.get_balance(self.address)
                if balance < loop(open_draw.payout):
                    raise Exception('not enough ICX balance')
                ###################################################
                winner = self.__pick_winner()
                if winner:
                    address = Address.from_string(winner.address)
                    self.icx.transfer(address, loop(winner.payout))
                    self._draws.save(self._open_draw)
                    self.__open_draw()
                else:
                    raise Exception('winner or ticket not found')
                ###################################################
        except Exception as e:
            revert(f'Unable to proceed the next draw : {str(e)}')

    def __pick_winner(self):
        db = self._db
        it = self._it
        players = self._players
        winners = self._winners
        open_draw = self._open_draw
        ticket = self.__random_ticket()

        winner = winners.create()
        winner.played = ticket.amount
        winner.address = ticket.address
        winner.timestamp = it.timestamp
        winner.payout = open_draw.payout
        winner.tx_count = ticket.tx_count
        winner.draw_number = str(open_draw.number)
        winner.chance = ticket.amount / open_draw.prize
        winners.save(winner)
        
        player = players[winner.address]
        player.total_payout += winner.payout
        players.save(player)

        open_draw.winner = winner.address
        open_draw.save(db)

        return winner

    def __open_draw(self):
        db = self._db
        it = self._it
        draws = self._draws
        open_draw = OpenDraw()
        open_draw.block = it.block
        last_draw = draws.get_last()
        open_draw.timestamp = it.timestamp
        open_draw.fill(VarDB(DRAW_CONF_VAR, db, str).get())
        open_draw.number = str(int(last_draw.number) + 1 if last_draw else 1000)
        open_draw.save(db)
        self._open_draw = open_draw

    def __random_ticket(self):
        it = self._it
        tickets = self._tickets
        open_draw = self._open_draw
        chances = [ticket.amount / open_draw.prize for ticket in tickets]
        seed = f'{str(it)}_{str(open_draw.prize)}_{str(open_draw.ticket_count)}'
        random = (int.from_bytes(sha3_256(seed.encode()), 'big') % 100000) / 100000.0
        factor = sum(chances) * random
        for index, chance in enumerate(chances):
            factor -= chance
            if factor < 0: return tickets.get(index)
        return None