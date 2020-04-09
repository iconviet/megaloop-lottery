from iconservice import *

TAG = 'IconLott'


class IconLott(IconScoreBase):
    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._players = ArrayDB('players', db, value_type=Address)
        self._players_record = DictDB('players_record', db, value_type=int)

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
        Logger.debug(message, TAG)
        return message

    @external(readonly=True)
    def ls_players(self) -> dict:
        players_record = {str(i): self._players_record[i] for i in self._players}
        return players_record
