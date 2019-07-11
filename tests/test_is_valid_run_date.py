import unittest
from espresso import is_valid_run_date


class TestIsValidRunDate(unittest.TestCase):

    def test_valid_dates(self):
        self.assertTrue(is_valid_run_date("2019-07-10"))
        self.assertTrue(is_valid_run_date("2019-07-10T21:09:25+00:00"))
        self.assertTrue(is_valid_run_date("2019-07-10T21:09:25Z"))
        self.assertTrue(is_valid_run_date("20190710T210925Z"))
        self.assertTrue(is_valid_run_date("2019-07-10T21:09:25+0000"))
