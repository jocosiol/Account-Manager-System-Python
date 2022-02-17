import unittest
import requests
import application

class TestApplication(unittest.TestCase):
    #URLS
    API_URL = "http://127.0.0.1:5000"
    ACCOUNT_URL = "{}/account".format(API_URL)
    CREATE_ACCOUNT_URL = "{}/account/create".format(API_URL)

    #OBJECTS
    NEW_ACCOUNT_OBJ = {
    "name": "James B",
    "document": "007",
    "dailyWithdrawLimit": "500",
    "accountType": "100"
}

    def test_1_get_accounts(self):
        r = requests.get(TestApplication.ACCOUNT_URL)
        self.assertEqual(r.status_code, 200)

    def test_2_create_new_account(self):
        r = requests.post(TestApplication.CREATE_ACCOUNT_URL, json=TestApplication.NEW_ACCOUNT_OBJ)
        self.assertEqual(r.status_code, 200)
    
    