from ..megaloop import Megaloop
from tbears.libs.scoretest.score_test_case import ScoreTestCase

from pprint import pprint


class TestMegaloop(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.score = self.get_score_instance(Megaloop, self.test_account1)
