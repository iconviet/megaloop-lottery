from iconservice import *

TAG = 'IconvietLottery'

DEFAULT_POT_LIMIT = 2000 * 10 ** 18  # 2000 ICX
DEFAULT_COMMISSION = 5  # 5%
DEFAULT_DEPOSIT_SIZE_LIMIT = 150  # 150%


class IconLott(IconScoreBase):
    """
    Lightpaper: https://github.com/duyyudus/icon-lottery
    """

    _SCORE_NAME = 'ICONVIET Probabilistic Lottery'

    BUFFER_FUND = 5 * 10 ** 18  # 5 ICX

    # Round-wise
    _PLAYERS = 'players'
    _PLAYERS_RECORD = 'players_record'
    _MONEY_POT = 'money_pot'
    _TOP_DEPOSIT = 'top_deposit'

    # History
    _LAST_SETTLEMENT_BH = 'last_settlement_bh'
    _LAST_WINNER = 'last_winner'

    # Governance variables
    _POT_LIMIT = 'pot_limit'
    _COMMISSION = 'commission'
    _DEPOSIT_SIZE_LIMIT = 'deposit_size_limit'
    _TREASURY = 'treasury'

    @eventlog
    def WinnerFundTransfer(self, player: Address, amount: int):
        pass

    @eventlog
    def TreasuryFundTransfer(self, amount: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._players = ArrayDB(self._PLAYERS, db, value_type=Address)
        self._players_record = DictDB(self._PLAYERS_RECORD, db, value_type=int)
        self._money_pot = VarDB(self._MONEY_POT, db, value_type=int)
        self._top_deposit = VarDB(self._TOP_DEPOSIT, db, value_type=int)

        self._last_settlement_bh = VarDB(self._LAST_SETTLEMENT_BH, db, value_type=int)
        self._last_winner = VarDB(self._LAST_WINNER, db, value_type=Address)

        self._pot_limit = VarDB(self._POT_LIMIT, db, value_type=int)
        self._commission = VarDB(self._COMMISSION, db, value_type=int)
        self._deposit_size_limit = VarDB(self._DEPOSIT_SIZE_LIMIT, db, value_type=int)
        self._treasury = VarDB(self._TREASURY, db, value_type=Address)

    def on_install(self) -> None:
        super().on_install()

        self._money_pot.set(0)
        self._top_deposit.set(0)

        self._last_settlement_bh.set(0)

        self._pot_limit.set(DEFAULT_POT_LIMIT)
        self._commission.set(DEFAULT_COMMISSION)
        self._deposit_size_limit.set(DEFAULT_DEPOSIT_SIZE_LIMIT)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return self._SCORE_NAME

    ###############################################################################################
    # Governance variables

    @external
    def set_pot_limit(self, pot_limit: int) -> None:
        """
        In `loop` unit, e.g `1000 * 10 ** 18` loops = `1000` ICX
        """
        if self.msg.sender == self.owner:
            self._pot_limit.set(pot_limit)

    @external(readonly=True)
    def get_pot_limit(self) -> int:
        """
        In `loop` unit, e.g `1000 * 10 ** 18` loops = `1000` ICX
        """
        return self._pot_limit.get()

    @external
    def set_commission(self, commission: int) -> None:
        """
        In percentage unit, e.g. `5` %
        """

        if self.msg.sender == self.owner:
            self._commission.set(commission)

    @external(readonly=True)
    def get_commission(self) -> int:
        """
        In percentage unit, e.g. `5` %
        """
        return self._commission.get()

    @external
    def set_deposit_size_limit(self, deposit_size_limit: int) -> None:
        """
        In percentage unit, e.g. `150` %
        """

        if self.msg.sender == self.owner:
            self._deposit_size_limit.set(deposit_size_limit)

    @external(readonly=True)
    def get_deposit_size_limit(self) -> int:
        """
        In percentage unit, e.g. `150` %
        """
        return self._deposit_size_limit.get()

    @external
    def set_treasury(self, treasury_address: Address) -> None:
        if self.msg.sender == self.owner:
            self._treasury.set(treasury_address)

    @external(readonly=True)
    def get_treasury(self) -> Address:
        return self._treasury.get()

    # End of governance variables
    ###############################################################################################

    ###############################################################################################
    # Deposit and money pot

    @external(readonly=True)
    def money_pot_balance(self) -> int:
        return self._money_pot.get()

    @external(readonly=True)
    def get_top_deposit(self) -> int:
        return self._top_deposit.get()

    @payable
    def fallback(self):
        """
        Accept ICX sent by anyone.
        """
        if self.msg.sender == self.owner:
            # Always receive ICX from owner wallet
            pass
        elif self.msg.sender in self._players:
            revert(f'{self.msg.sender} is already in player list')
        elif self.msg.value + self._money_pot.get() > self._pot_limit.get():
            revert(f'New deposit exceeds limit of money pot')
        elif self._last_settlement_bh.get() == self.block_height:
            revert('Failed due to current block contains winner selection transaction')
        elif self.msg.value == 0:
            revert('Zero deposit is not allowed')
        elif self._top_deposit.get() > 0:
            limit = self._deposit_size_limit.get()
            if self.msg.value > limit * self._top_deposit.get() / 100:
                revert(
                    f'Deposit size must not be {limit}% greater than top deposit recorded in current round, which is {self._top_deposit.get()/10**18} ICX'
                )

        if self.msg.sender != self.owner:
            try:
                self._players.put(self.msg.sender)
                self._players_record[self.msg.sender] = self.msg.value

                # New high record
                if self.msg.value > self._top_deposit.get():
                    self._top_deposit.set(self.msg.value)

                # Update money pot
                self._money_pot.set(self._money_pot.get() + self.msg.value)

                message = f'Received {self.msg.value/10**18} ICX from {self.msg.sender}'
                Logger.debug(message, TAG)
            except Exception as e:
                revert(f'Failed to receive ICX due to error: {str(e)}')

    # End of deposit
    ###############################################################################################

    ###############################################################################################
    # Draw winner

    def _new_round(self) -> None:
        self._money_pot.set(0)
        self._top_deposit.set(0)
        self._last_settlement_bh.set(self.block_height)

        while len(self._players) > 0:
            self._players.pop()

    def _random(self) -> float:
        """
        Generate a random number in range [0, 1) from `TX_HASH` + `TIMESTAMP` + `len(PLAYERS)` + `MONEY_POT`
        """
        seed = (
            str(bytes.hex(self.tx.hash))
            + str(self.now)
            + str(len(self._players))
            + str(self._money_pot.get())
        )
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
    def select_winner(self) -> None:
        if self.msg.sender != self.owner:
            revert('Only contract owner is allowed to select winner')
        elif len(self._players) < 2:
            revert('There must be at least 2 players in current round')
        elif not self._money_pot.get() > 0:
            revert('Money pot must be greater than zero')

        money_pot = self._money_pot.get()
        commission = self._commission.get()

        winner_value = (100 - commission) * money_pot // 100
        commission_value = commission * money_pot // 100
        required = winner_value + commission_value + self.BUFFER_FUND
        contract_balance = self.icx.get_balance(self.address)
        if contract_balance < required:
            revert(
                f'Not enough fund in the contract. Balance is {contract_balance/10**18} ICX, require {required/10**18} ICX'
            )

        try:
            weights = [self._players_record[i] / money_pot for i in self._players]
            winner_id = self._weighted_random(weights)
            if winner_id is not None:
                winner_address = self._players.get(winner_id)
                self.icx.transfer(winner_address, winner_value)
                # self.WinnerFundTransfer(winner_address, winner_value)
                self._last_winner.set(winner_address)

            treasury_address = self._treasury.get()
            if treasury_address is not None:
                self.icx.transfer(treasury_address, commission_value)
                # self.TreasuryFundTransfer(commission_value)

            # New game
            self._new_round()

        except Exception as e:
            revert(f'Failed to draw winner due to error: {str(e)}')

    @external(readonly=True)
    def get_last_winner(self) -> Address:
        return self._last_winner.get()

    # End of select winner
    ###############################################################################################

    ###############################################################################################
    # Misc

    @external(readonly=True)
    def about(self) -> str:
        message = 'Welcome to ICONLOTT, a product of ICONVIET'
        return message

    @external(readonly=True)
    def ls_players(self) -> dict:
        players_record = {str(i): self._players_record[i] for i in self._players}
        return players_record

    # End of misc
    ###############################################################################################
