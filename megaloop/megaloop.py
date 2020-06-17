from iconservice import *

class Megaloop(IconScoreBase):
        
    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v1.1.0'

    def on_update(self):
        super().on_update()
    
    def on_install(self):
        super().on_install()
        
        self._comm_rate.set(0)        
        self._draw_prize.set(0)
        self._last_draw_bh.set(0)        
        self._is_enabled.set(True)
        self._sponsors.put(self.owner)
        self._max_grant.set(5 * 10 ** 18)
        self._prize_limit.set(1000 * 10 ** 18)    

    def __init__(self, db: IconScoreDatabase):
        super().__init__(db)
        
        self._winners = ArrayDB('winners', db, value_type=str)
        self._players = ArrayDB('players', db, value_type=Address)
        self._sponsors = ArrayDB('sponsor', db, value_type=Address)

        self._comm_rate = VarDB('comm_rate', db, value_type=int)
        self._max_grant = VarDB('max_grant', db, value_type=int)
        self._draw_prize = VarDB('draw_prize', db, value_type=int)
        self._is_enabled = VarDB('is_enabled', db, value_type=bool)
        self._prize_limit = VarDB('prize_limit', db, value_type=int)
        self._last_winner = VarDB('last_winner', db, value_type=str)
        self._last_draw_bh = VarDB('last_draw_bh', db, value_type=int)
        self._last_draw_tx = VarDB('last_draw_tx', db, value_type=str)        
        self._last_player = VarDB('last_player', db, value_type=Address)
        self._comm_address = VarDB('comm_address', db, value_type=Address)
                
        self._player_blocks = DictDB('player_blocks', db, value_type=str)
        self._player_tickets = DictDB('player_tickets', db, value_type=int)

    #######################################################################

    @payable
    def fallback(self):
        self.set_fee_sharing_proportion(100)        
        if self.msg.sender in self._sponsors:
            return
        if self.msg.value == 0:
            revert('Zero value is not allowed')
        if not self._is_enabled.get():
            revert('Contract is currently disabled')
        if self._last_draw_bh.get() == self.block_height:
            revert('Draw is in process. Play is not allowed')
        try:
            if self.msg.sender not in self._players:
                ticket = self.msg.value
                self._players.put(self.msg.sender)
                self._player_tickets[self.msg.sender] = ticket
            else:
                last_ticket = self._player_tickets[self.msg.sender]
                next_ticket = last_ticket + self.msg.value
                self._player_tickets[self.msg.sender] = next_ticket
            self._last_player.set(self.msg.sender)
            self._player_blocks[self.msg.sender] = str(self.block_height)
            self._draw_prize.set(self._draw_prize.get() + self.msg.value)
        except Exception as e:
            revert(f'Unable to process your transaction. Error: {str(e)}')
    
    ######################################################################

    @external
    def add_sponsor(self, address: Address):
        if address not in self._sponsors:
            self._sponsors.put(address)

    @external(readonly=True)
    def get_sponsors(self) -> list:
        return [str(i) for i in self._sponsors]

    @external
    def set_max_grant(self, max_grant: int):
        if self.msg.sender == self.owner:
            self._max_grant.set(max_grant)

    @external(readonly=True)
    def get_max_grant(self) -> str:
        return str(self._max_grant.get())

    @external
    def set_prize_limit(self, prize_limit: int):
        if self.msg.sender == self.owner:
            self._prize_limit.set(prize_limit)

    @external(readonly=True)
    def get_prize_limit(self) -> str:
        return str(self._prize_limit.get())

    @external
    def set_comm_rate(self, comm_rate: int):        
        if self.msg.sender == self.owner:
            self._comm_rate.set(comm_rate)

    @external(readonly=True)
    def get_comm_rate(self) -> str:
        return str(self._comm_rate.get())
    
    @external
    def set_comm_address(self, address: Address):
        if self.msg.sender == self.owner:
            self._comm_address.set(address)

    @external(readonly=True)
    def get_comm_address(self) -> Address:
        return self._comm_address.get()

    @external
    def set_is_enabled(self, enabled: bool):
        if self.msg.sender == self.owner:
            self._is_enabled.set(enabled)

    @external(readonly=True)
    def get_is_enabled(self) -> bool:
        return self._is_enabled.get()
    
    @external(readonly=True)
    def get_draw_prize(self) -> str:
        return str(self._draw_prize.get())

    @external(readonly=True)
    def get_last_winner(self) -> str:
        """
        Returns:
            str: "<block>:<address>:<ticket>:<draw_prize>:<draw_grant>"
        """
        return self._last_winner.get()

    @external(readonly=True)
    def get_last_draw_bh(self) -> str:
        return str(self._last_draw_bh.get())

    @external(readonly=True)
    def get_last_draw_tx(self) -> str:
        return self._last_draw_tx.get()

    @external(readonly=True)
    def get_winners(self) -> list:
        return [str(winner) for winner in self._winners]

    @external(readonly=True)
    def get_draw_grant(self) -> str:
        comm_rate = self._comm_rate.get()
        max_grant = self._max_grant.get()
        draw_prize = self._draw_prize.get()
        prize_limit = self._prize_limit.get()
        real_draw_prize = (100 - comm_rate) * draw_prize // 100
        draw_grant = prize_limit - real_draw_prize if real_draw_prize < prize_limit else 0
        draw_grant = draw_grant if draw_grant < max_grant else max_grant
        return str(draw_grant)

    @external(readonly=True)
    def get_players(self) -> list:
        """
        Returns:
            list: format
                [
                    "<address>:<ticket>:<block>",
                    ...
                ]
        """
        return [
            f'{str(i)}:{self._player_tickets[i]}:{self._player_blocks[i]}' for i in self._players
        ]

    @external(readonly=True)
    def get_player(self, address: Address) -> str:
        """
        Returns:
            str: "<address>:<ticket>:<block>"
        """
        if address in self._players:
            return (
                f'{str(address)}:{self._player_tickets[address]}:{self._player_blocks[address]}'
            )

    @external(readonly=True)
    def get_last_player(self) -> str:
        """
        Returns:
            str: "<address>:<ticket>:<block>"
        """
        addr = self._last_player.get()
        if addr:
            return f'{str(addr)}:{self._player_tickets[addr]}:{self._player_blocks[addr]}'

    ###########################################################################

    def _start_new_round(self):
        self._players = []
        self._draw_prize.set(0)
        self._player_blocks = []
        self._player_tickets = []
        self._last_player.remove()
        self._last_draw_bh.set(self.block_height)
        self._last_draw_tx.set(f'0x{bytes.hex(self.tx.hash)}')

    def _random(self) -> float:
        """
        Generate a random number in range [0, 1) from `TX_HASH` + `len(PLAYERS)` + `JACKPOT`
        """
        seed = str(bytes.hex(self.tx.hash)) + str(len(self._players)) + str(self._draw_prize.get()) + str(self.now())
        rand = int.from_bytes(sha3_256(seed.encode()), 'big') % 100000
        return rand / 100000.0

    def _calculate_weighted_random(self, weights: list) -> int:
        """
        Linear scan weighted random choice ( weight is probability )
        """
        remaining_distance = self._random() * sum(weights)
        for i, w in enumerate(weights):
            remaining_distance -= w
            if remaining_distance < 0:
                return i

    @external
    def draw_winner(self):
        if self.msg.sender != self.owner:
            revert('Only contract owner is allowed to select winner')
        elif len(self._players) == 0:
            self._start_new_round()
        elif len(self._players) == 1:
            revert('There must be at least 2 players in current round')
        elif not self._draw_prize.get() > 0:
            revert('Prize must be greater than zero')
        else:
            comm_rate = self._comm_rate.get()
            max_grant = self._max_grant.get()
            draw_prize = self._draw_prize.get()            
            prize_limit = self._prize_limit.get()

            # calculate comm.
            comm_value = draw_prize * comm_rate  // 100

            # calculate prize
            real_draw_prize = draw_prize * (100 - comm_rate) // 100
            draw_grant = prize_limit - real_draw_prize if real_draw_prize < prize_limit else 0
            draw_grant = draw_grant if draw_grant < max_grant else max_grant
            real_draw_prize = real_draw_prize + draw_grant

            icx_minimum = real_draw_prize + comm_value
            icx_balance = self.icx.get_balance(self.address)
            if icx_balance < icx_minimum:
                revert(f'Insufficient fund. Current balance is {icx_balance/10**18} ICX, {icx_minimum/10**18} ICX is required')
            
            try:
                weights = [self._player_tickets[i] / draw_prize for i in self._players]
                winner_id = self._calculate_weighted_random(weights)
                
                if winner_id is not None:
                    winner_address = self._players.get(winner_id)
                    self.icx.transfer(winner_address, real_draw_prize)
                    winners = f'{self.block_height}:{winner_address}:{self._player_tickets[winner_address]}:{real_draw_prize}:{draw_grant}'                    
                    self._last_winner.set(winners)
                    self._winners.put(winners)

                comm_address = self._comm_address.get()
                if comm_address is not None and comm_value > 0:
                    self.icx.transfer(comm_address, comm_value)

                self._start_new_round()

            except Exception as e:
                revert(f'Unable to draw winner. Error: {str(e)}')

    ###########################################################################