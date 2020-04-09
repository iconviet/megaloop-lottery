from ..iconlott import IconLott
from tbears.libs.scoretest.score_test_case import ScoreTestCase

from pprint import pprint


class TestIconLott(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(IconLott, self.test_account1)

    def test_ls_players(self):
        pass
        # pprint(self.score.ls_players())
        # self.assertEqual(self.score.hello(), "Hello")
