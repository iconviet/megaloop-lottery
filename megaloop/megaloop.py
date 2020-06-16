from iconservice import *

class Megaloop(IconScoreBase):
    
    @external(readonly=True)
    def name(self) -> str:
        return 'MEGALOOP v1.0.0'

    def on_update(self) -> None:
        super().on_update()

    def on_install(self) -> None:
        super().on_install()

        self._prize.set(0)
        self._comm_rate.set(0)
        self._enabled.set(True)
        self._last_draw_bh.set(0)
        self._sponsors.put(self.owner)
        self._max_subsidy.set(50 * 10 ** 18)
        self._prize_limit.set(1000 * 10 ** 18)    

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        
        # VarDB
        self._prize = VarDB('prize', db, value_type=int)
        self._enabled = VarDB('enabled', db, value_type=bool)
        self._comm_rate = VarDB('comm_rate', db, value_type=int)
        self._max_subsidy = VarDB('max_subsidy', db, value_type=int)
        self._prize_limit = VarDB('prize_limit', db, value_type=int)
        self._last_winner = VarDB('last_winner', db, value_type=str)
        self._last_draw_bh = VarDB('last_draw_bh', db, value_type=int)
        self._last_draw_tx = VarDB('last_draw_tx', db, value_type=str)
        self._last_player = VarDB('last_player', db, value_type=Address)
        self._comm_address = VarDB('comm_address', db, value_type=Address)
        
        # ArrayDB
        self._players = ArrayDB('players', db, value_type=Address)
        self._sponsors = ArrayDB('sponsor', db, value_type=Address)
        self._winner_records = ArrayDB('winner_records', db, value_type=str)

        # DictDB
        self._player_records = DictDB('player_records', db, value_type=str)
        self._player_deposits = DictDB('player_deposits', db, value_type=int)

    #########################################################################
    
    @external
    def add_sponsor(self, address: Address) -> None:
        if address not in self._sponsors:
            self._sponsors.put(address)

    @external(readonly=True)
    def get_sponsors(self) -> list:
        addresses = [str(i) for i in self._sponsors]
        return addresses

    @external
    def set_max_subsidy(self, max_subsidy: int) -> None:
        if self.msg.sender == self.owner:
            self._max_subsidy.set(max_subsidy)

    @external(readonly=True)
    def get_max_subsidy(self) -> str:
        return str(self._max_subsidy.get())

    @external
    def set_prize_limit(self, prize_limit: int) -> None:
        if self.msg.sender == self.owner:
            self._prize_limit.set(prize_limit)

    @external(readonly=True)
    def get_prize_limit(self) -> str:
        return str(self._prize_limit.get())

    @external
    def set_comm_rate(self, comm_rate: int) -> None:        
        if self.msg.sender == self.owner:
            self._comm_rate.set(comm_rate)

    @external(readonly=True)
    def get_comm_rate(self) -> str:
        return str(self._comm_rate.get())
    
    @external
    def set_comm_address(self, address: Address) -> None:
        if self.msg.sender == self.owner:
            self._comm_address.set(address)

    @external(readonly=True)
    def get_comm_address(self) -> Address:
        return self._comm_address.get()

    @external
    def set_enabled(self, enabled: bool) -> None:
        if self.msg.sender == self.owner:
            self._enabled.set(enabled)

    @external(readonly=True)
    def get_enabled(self) -> bool:
        return self._enabled.get()
    
    @external(readonly=True)
    def get_prize(self) -> str:
        return str(self._prize.get())

    @payable
    def fallback(self):
        """
        Accept ICX sent by anyone.
        """
        if self.msg.sender in self._sponsors:
            # Always receive ICX from sponsors
            pass
        elif not self._enabled.get():
            revert('Megaloop is currently disabled')
        elif self.msg.value + self._prize.get() > self._prize_limit.get():
            revert(f'Deposit exceeded prize limit')
        elif self._last_draw_bh.get() == self.block_height:
            revert('Failed due to current block contains winner drawing transaction')
        elif self.msg.value == 0:
            revert('Zero deposit is not allowed')
        else:
            try:
                if self.msg.sender not in self._players:
                    self._players.put(self.msg.sender)
                    bet_size = self.msg.value
                    self._player_deposits[self.msg.sender] = bet_size
                else:
                    current_amount = self._player_deposits[self.msg.sender]
                    bet_size = current_amount + self.msg.value
                    self._player_deposits[self.msg.sender] = bet_size

                # Update prize
                self._prize.set(self._prize.get() + self.msg.value)

                # Update last player
                self._last_player.set(self.msg.sender)

                # Update player record
                self._player_records[self.msg.sender] = str(self.block_height)
            
            except Exception as e:
                revert(f'Failed to receive ICX due to error: {str(e)}')

    ###############################################################################################
    # Draw winner

    def _new_round(self) -> None:
        self._prize.set(0)
        self._last_player.remove()
        self._last_draw_bh.set(self.block_height)
        self._last_draw_tx.set(f'0x{bytes.hex(self.tx.hash)}')

        while len(self._players) > 0:
            self._players.pop()

    def _random(self) -> float:
        """
        Generate a random number in range [0, 1) from `TX_HASH` + `len(PLAYERS)` + `JACKPOT`
        """
        seed = str(bytes.hex(self.tx.hash)) + str(len(self._players)) + str(self._prize.get()) + str(self.now())
        rand = int.from_bytes(sha3_256(seed.encode()), 'big') % 100000
        return rand / 100000.0

    def _weighted_random(self, weights: list) -> int:
        """
        Linear scan weighted random choice ( weight is probability )
        """
        remaining_distance = self._random() * sum(weights)
        for i, w in enumerate(weights):
            remaining_distance -= w
            if remaining_distance < 0:
                return i

    @external
    def draw_winner(self) -> None:
        if self.msg.sender != self.owner:
            revert('Only contract owner is allowed to select winner')
        elif len(self._players) == 0:
            self._new_round()
        elif len(self._players) == 1:
            revert('There must be at least 2 players in current round')
        elif not self._prize.get() > 0:
            revert('Prize must be greater than zero')
        else:
            prize = self._prize.get()
            comm_rate = self._comm_rate.get()
            max_subsidy = self._max_subsidy.get()
            prize_limit = self._prize_limit.get()

            # Calculate commision
            comm_rate_value = comm_rate * prize // 100

            # Calculate prize
            prize_value = (100 - comm_rate) * prize // 100
            subsidized = prize_limit - prize_value if prize_value < prize_limit else 0
            subsidized = subsidized if subsidized < max_subsidy else max_subsidy
            prize_value = prize_value + subsidized

            required = prize_value + comm_rate_value
            contract_balance = self.icx.get_balance(self.address)
            if contract_balance < required:
                revert(
                    f'Not enough fund in the contract. Balance is {contract_balance/10**18} ICX, require {required/10**18} ICX'
                )

            try:
                weights = [self._player_deposits[i] / prize for i in self._players]
                winner_id = self._weighted_random(weights)
                if winner_id is not None:
                    winner_address = self._players.get(winner_id)
                    self.icx.transfer(winner_address, prize_value)
                    winner_records = f'{self.block_height}:{winner_address}:{self._player_deposits[winner_address]}:{prize_value}:{subsidized}'                    
                    self._last_winner.set(winner_records)
                    self._winner_records.put(winner_records)

                comm_address_address = self._comm_address.get()
                if comm_address_address is not None and comm_rate_value > 0:
                    self.icx.transfer(comm_address_address, comm_rate_value)

                # New game
                self._new_round()

            except Exception as e:
                revert(f'Failed to draw winner due to error: {str(e)}')

    @external(readonly=True)
    def get_last_winner(self) -> str:
        """
        Returns:
            str: "<block_height>:<address>:<deposit_size>:<total_prize_value>:<subsidy_value>"
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
        return [str(addr) for addr in self._winner_records]

    @external(readonly=True)
    def get_subsidy(self) -> str:
        prize = self._prize.get()
        comm_rate = self._comm_rate.get()
        max_subsidy = self._max_subsidy.get()
        prize_limit = self._prize_limit.get()
        prize_value = (100 - comm_rate) * prize // 100
        subsidized = prize_limit - prize_value if prize_value < prize_limit else 0
        subsidized = subsidized if subsidized < max_subsidy else max_subsidy

        return str(subsidized)

    # End of select winner
    ###############################################################################################

    @external(readonly=True)
    def get_players(self) -> list:
        """
        Returns:
            list: format
                [
                    "<address>:<deposit_amount>:<block_height>",
                    ...
                ]
        """
        player_records = [
            f'{str(i)}:{self._player_deposits[i]}:{self._player_records[i]}' for i in self._players
        ]
        return player_records

    @external(readonly=True)
    def get_player(self, address: Address) -> str:
        """
        Returns:
            str: "<address>:<deposit_amount>:<block_height>"
        """
        if address in self._players:
            return (
                f'{str(address)}:{self._player_deposits[address]}:{self._player_records[address]}'
            )

    @external(readonly=True)
    def get_last_player(self) -> str:
        """
        Returns:
            str: "<address>:<deposit_amount>:<block_height>"
        """
        addr = self._last_player.get()
        if addr:
            return f'{str(addr)}:{self._player_deposits[addr]}:{self._player_records[addr]}'