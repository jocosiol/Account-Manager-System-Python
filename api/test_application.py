import unittest
import requests
import application

class TestApplication(unittest.TestCase):
    API_URL = "http://127.0.0.1:5000"
    BALANCE_URL = "{}/account".format(API_URL)

    def test_1_get_accounts(self):
        r = requests.get(TestApplication.BALANCE_URL)
        self.assertEqual(r.status_code, 200)
