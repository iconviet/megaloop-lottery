from iconservice import *

TAG = 'IconvietMegaloop'

DEFAULT_MAX_SUBSIDY = 400 * 10 ** 18  # 400 ICX
DEFAULT_POT_LIMIT = 1000 * 10 ** 18  # 1000 ICX
DEFAULT_COMMISSION = 0  # 0%, no commission
DEFAULT_DEPOSIT_SIZE_LIMIT = 150  # 150%


class Megaloop(IconScoreBase):
    """
    Lightpaper: https://github.com/duyyudus/icon-lottery
    """

    _SCORE_NAME = 'ICONVIET MEGALOOP'

    BUFFER_FUND = 5 * 10 ** 18  # 5 ICX

    # Round-wise
    _PLAYERS = 'players'
    _PLAYERS_DEPOSIT = 'players_deposit'
    _PLAYERS_RECORD = 'players_record'
    _JACKPOT = 'jackpot'
    _TOP_DEPOSIT = 'top_deposit'
    _LAST_PLAYER = 'last_player'

    # History
    _LAST_SETTLEMENT_BH = 'last_settlement_bh'
    _LAST_SETTLEMENT_TX = 'last_settlement_tx'
    _LAST_WINNER = 'last_winner'

    # Governance variables
    _NON_PLAYERS = 'non_players'
    _MAX_SUBSIDY = 'max_subsidy'
    _POT_LIMIT = 'pot_limit'
    _COMMISSION = 'commission'
    _DEPOSIT_SIZE_LIMIT = 'deposit_size_limit'
    _PROFIT_HOLDER = 'profit_holder'
    _ENABLED = 'enabled'

    @eventlog
    def WinnerRecord(self, winner_record: str):
        pass

    @eventlog
    def ProfitRecord(self, amount: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._players = ArrayDB(self._PLAYERS, db, value_type=Address)
        self._players_deposit = DictDB(self._PLAYERS_DEPOSIT, db, value_type=int)
        self._players_record = DictDB(self._PLAYERS_RECORD, db, value_type=str)
        self._jackpot = VarDB(self._JACKPOT, db, value_type=int)
        self._top_deposit = VarDB(self._TOP_DEPOSIT, db, value_type=int)
        self._last_player = VarDB(self._LAST_PLAYER, db, value_type=Address)

        self._last_settlement_bh = VarDB(self._LAST_SETTLEMENT_BH, db, value_type=int)
        self._last_settlement_tx = VarDB(self._LAST_SETTLEMENT_TX, db, value_type=str)
        self._last_winner = VarDB(self._LAST_WINNER, db, value_type=str)

        self._non_players = ArrayDB(self._NON_PLAYERS, db, value_type=Address)
        self._max_subsidy = VarDB(self._MAX_SUBSIDY, db, value_type=int)
        self._pot_limit = VarDB(self._POT_LIMIT, db, value_type=int)
        self._commission = VarDB(self._COMMISSION, db, value_type=int)
        self._deposit_size_limit = VarDB(self._DEPOSIT_SIZE_LIMIT, db, value_type=int)
        self._profit_holder = VarDB(self._PROFIT_HOLDER, db, value_type=Address)
        self._enabled = VarDB(self._ENABLED, db, value_type=bool)

    def on_install(self) -> None:
        super().on_install()

        self._jackpot.set(0)
        self._top_deposit.set(0)

        self._last_settlement_bh.set(0)

        self._non_players.put(self.owner)
        self._max_subsidy.set(DEFAULT_MAX_SUBSIDY)
        self._pot_limit.set(DEFAULT_POT_LIMIT)
        self._commission.set(DEFAULT_COMMISSION)
        self._deposit_size_limit.set(DEFAULT_DEPOSIT_SIZE_LIMIT)
        self._enabled.set(True)

    def on_update(self) -> None:
        super().on_update()

        if self.owner not in self._non_players:
            self._non_players.put(self.owner)
        self._max_subsidy.set(DEFAULT_MAX_SUBSIDY)
        self._pot_limit.set(DEFAULT_POT_LIMIT)
        self._commission.set(DEFAULT_COMMISSION)
        self._deposit_size_limit.set(DEFAULT_DEPOSIT_SIZE_LIMIT)

    @external(readonly=True)
    def name(self) -> str:
        return self._SCORE_NAME

    ###############################################################################################
    # Governance variables

    @external
    def add_non_player(self, address: Address) -> None:
        if address not in self._non_players:
            self._non_players.put(address)

    @external(readonly=True)
    def ls_non_players(self) -> list:
        addresses = [str(i) for i in self._non_players]
        return addresses

    @external
    def set_max_subsidy(self, max_subsidy: int) -> None:
        if self.msg.sender == self.owner:
            self._max_subsidy.set(max_subsidy)

    @external(readonly=True)
    def get_max_subsidy(self) -> str:
        return str(self._max_subsidy.get())

    @external
    def set_pot_limit(self, pot_limit: int) -> None:
        """
        In `loop` unit, e.g `1000 * 10 ** 18` loops = `1000` ICX
        """
        if self.msg.sender == self.owner:
            self._pot_limit.set(pot_limit)

    @external(readonly=True)
    def get_pot_limit(self) -> str:
        """
        In `loop` unit, e.g `1000 * 10 ** 18` loops = `1000` ICX
        """
        return str(self._pot_limit.get())

    @external
    def set_commission(self, commission: int) -> None:
        """
        In percentage unit, e.g. `5` %
        """

        if self.msg.sender == self.owner:
            self._commission.set(commission)

    @external(readonly=True)
    def get_commission(self) -> str:
        """
        In percentage unit, e.g. `5` %
        """
        return str(self._commission.get())

    @external
    def set_deposit_size_limit(self, deposit_size_limit: int) -> None:
        """
        In percentage unit, e.g. `150` %
        """

        if self.msg.sender == self.owner:
            self._deposit_size_limit.set(deposit_size_limit)

    @external(readonly=True)
    def get_deposit_size_limit(self) -> str:
        """
        In percentage unit, e.g. `150` %
        """
        return str(self._deposit_size_limit.get())

    @external
    def set_profit_holder(self, address: Address) -> None:
        if self.msg.sender == self.owner:
            self._profit_holder.set(address)

    @external(readonly=True)
    def get_profit_holder(self) -> Address:
        return self._profit_holder.get()

    @external
    def enable_contract(self, enabled: bool) -> None:
        if self.msg.sender == self.owner:
            self._enabled.set(enabled)

    @external(readonly=True)
    def is_enabled(self) -> bool:
        return self._enabled.get()

    # End of governance variables
    ###############################################################################################

    ###############################################################################################
    # Deposit and jackpot

    @external(readonly=True)
    def get_jackpot_size(self) -> str:
        return str(self._jackpot.get())

    @external(readonly=True)
    def get_top_deposit(self) -> str:
        return str(self._top_deposit.get())

    @payable
    def fallback(self):
        """
        Accept ICX sent by anyone.
        """
        if self.msg.sender in self._non_players:
            # Always receive ICX from non-player wallets
            pass
        elif not self._enabled.get():
            revert('Lottery contract is currently disabled')
        elif self.msg.value + self._jackpot.get() > self._pot_limit.get():
            revert(f'New deposit exceeds limit of money pot')
        elif self._last_settlement_bh.get() == self.block_height:
            revert('Failed due to current block contains winner drawing transaction')
        elif self.msg.value == 0:
            revert('Zero deposit is not allowed')

        # Temporarily disable DEPOSIT SIZE LIMIT check
        # elif self._top_deposit.get() > 0:
        #     limit = self._deposit_size_limit.get()
        #     if self.msg.value > limit * self._top_deposit.get() / 100:
        #         revert(
        #             f'Deposit size must not be {limit}% greater than top deposit recorded in current round, which is {self._top_deposit.get()/10**18} ICX'
        #         )

        else:
            try:
                if self.msg.sender not in self._players:
                    self._players.put(self.msg.sender)
                    bet_size = self.msg.value
                    self._players_deposit[self.msg.sender] = bet_size
                else:
                    current_amount = self._players_deposit[self.msg.sender]
                    bet_size = current_amount + self.msg.value
                    self._players_deposit[self.msg.sender] = bet_size

                # New high record
                if bet_size > self._top_deposit.get():
                    self._top_deposit.set(bet_size)

                # Update jackpot
                self._jackpot.set(self._jackpot.get() + self.msg.value)

                # Update last player
                self._last_player.set(self.msg.sender)

                # Update player record
                self._players_record[self.msg.sender] = str(self.block_height)

                message = f'Received {self.msg.value/10**18} ICX from {self.msg.sender}'
                Logger.debug(message, TAG)
            except Exception as e:
                revert(f'Failed to receive ICX due to error: {str(e)}')

    # End of deposit
    ###############################################################################################

    ###############################################################################################
    # Draw winner

    def _new_round(self) -> None:
        self._jackpot.set(0)
        self._top_deposit.set(0)
        self._last_player.remove()
        self._last_settlement_bh.set(self.block_height)
        self._last_settlement_tx.set(f'0x{bytes.hex(self.tx.hash)}')

        while len(self._players) > 0:
            self._players.pop()

    def _random(self) -> float:
        """
        Generate a random number in range [0, 1) from `TX_HASH` + `len(PLAYERS)` + `JACKPOT`
        """
        seed = str(bytes.hex(self.tx.hash)) + str(len(self._players)) + str(self._jackpot.get())
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
        elif len(self._players) < 2:
            revert('There must be at least 2 players in current round')
        elif not self._jackpot.get() > 0:
            revert('Money pot must be greater than zero')

        jackpot = self._jackpot.get()
        commission = self._commission.get()
        max_subsidy = self._max_subsidy.get()
        pot_limit = self._pot_limit.get()

        # Calculate commision
        commission_value = commission * jackpot // 100

        # Calculate prize
        jackpot_value = (100 - commission) * jackpot // 100
        subsidized = pot_limit - jackpot_value if jackpot_value < pot_limit else 0
        subsidized = subsidized if subsidized < max_subsidy else max_subsidy
        prize_value = jackpot_value + subsidized

        required = prize_value + commission_value + self.BUFFER_FUND
        contract_balance = self.icx.get_balance(self.address)
        if contract_balance < required:
            revert(
                f'Not enough fund in the contract. Balance is {contract_balance/10**18} ICX, require {required/10**18} ICX'
            )

        try:
            weights = [self._players_deposit[i] / jackpot for i in self._players]
            winner_id = self._weighted_random(weights)
            if winner_id is not None:
                winner_address = self._players.get(winner_id)
                self.icx.transfer(winner_address, prize_value)
                winner_record = f'Winner: {winner_address} | Prize: {prize_value/10**18} ICX | Subsidy: {subsidized/10**18} ICX'
                self.WinnerRecord(winner_record)
                self._last_winner.set(
                    f'{winner_address}:{self._players_deposit[winner_address]}:{prize_value}:{subsidized}'
                )

            profit_holder_address = self._profit_holder.get()
            if profit_holder_address is not None and commission_value > 0:
                self.icx.transfer(profit_holder_address, commission_value)
                self.ProfitRecord(commission_value)

            # New game
            self._new_round()

        except Exception as e:
            revert(f'Failed to draw winner due to error: {str(e)}')

    @external(readonly=True)
    def get_last_winner(self) -> str:
        """
        Returns:
            str: "<address>:<deposit_size>:<total_prize_value>:<subsidy_value>"
        """
        return self._last_winner.get()

    @external(readonly=True)
    def get_last_settlement_bh(self) -> str:
        return str(self._last_settlement_bh.get())

    @external(readonly=True)
    def get_last_settlement_tx(self) -> str:
        return self._last_settlement_tx.get()

    # End of select winner
    ###############################################################################################

    ###############################################################################################
    # Misc

    @external(readonly=True)
    def about(self) -> str:
        message = 'Welcome to the MEGALOOP, a product of ICONVIET'
        return message

    @external(readonly=True)
    def ls_players(self) -> list:
        """
        Returns:
            list: format
                [
                    "<address>:<deposit_amount>:<block_height>",
                    ...
                ]
        """
        players_record = [
            f'{str(i)}:{self._players_deposit[i]}:{self._players_record[i]}' for i in self._players
        ]
        return players_record

    @external(readonly=True)
    def get_player(self, address: Address) -> str:
        """
        Returns:
            str: "<address>:<deposit_amount>:<block_height>"
        """
        if address in self._players:
            return (
                f'{str(address)}:{self._players_deposit[address]}:{self._players_record[address]}'
            )

    @external(readonly=True)
    def get_last_player(self) -> str:
        """
        Returns:
            str: "<address>:<deposit_amount>:<block_height>"
        """
        addr = self._last_player.get()
        if addr:
            return f'{str(addr)}:{self._players_deposit[addr]}:{self._players_record[addr]}'

    # End of misc
    ###############################################################################################
