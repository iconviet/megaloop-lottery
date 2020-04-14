from iconservice import *

TAG = 'IconLott'


class IconLott(IconScoreBase):
    _PLAYERS = 'players'
    _PLAYERS_RECORD = 'players_record'
    _MONEY_POT = 'money_pot'
    _LAST_SETTLEMENT_BH = 'last_settlement_bh'
    _TOP_DEPOSIT = 'top_deposit'

    # Governance variables
    _POT_LIMIT = 'pot_limit'
    _COMMISSION = 'commission'
    _DEPOSIT_SIZE_LIMIT = 'deposit_size_limit'
    _TREASURY = 'treasury'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._players = ArrayDB(self._PLAYERS, db, value_type=Address)
        self._players_record = DictDB(self._PLAYERS_RECORD, db, value_type=int)
        self._money_pot = VarDB(self._MONEY_POT, db, value_type=int)
        self._last_settlement_bh = VarDB(self._LAST_SETTLEMENT_BH, db, value_type=int)
        self._top_deposit = VarDB(self._TOP_DEPOSIT, db, value_type=int)

        self._pot_limit = VarDB(self._POT_LIMIT, db, value_type=int)
        self._commission = VarDB(self._COMMISSION, db, value_type=int)
        self._deposit_size_limit = VarDB(self._DEPOSIT_SIZE_LIMIT, db, value_type=int)
        self._treasury = VarDB(self._TREASURY, db, value_type=Address)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    @payable
    def fallback(self):
        """
        Accept ICX sent by anyone.
        """
        if self.msg.sender not in self._players:
            self._players.put(self.msg.sender)
            self._players_record[self.msg.sender] = self.msg.value
            message = f'Received {self.msg.value} ICX from {self.msg.sender}'
            Logger.debug(message, TAG)
        else:
            revert(f'{self.msg.sender} is already in player list')

    @external(readonly=True)
    def about(self) -> str:
        message = 'Welcome to ICONLOTT, a product of ICONVIET'
        return message

    @external(readonly=True)
    def ls_players(self) -> dict:
        players_record = {str(i): self._players_record[i] for i in self._players}
        return players_record

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
