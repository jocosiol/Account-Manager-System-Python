import unittest
import requests
import application
import json

class TestApplication(unittest.TestCase):
    #URLS
    API_URL = "http://127.0.0.1:5000"
    ACCOUNT_URL = "{}/account".format(API_URL)
    CREATE_ACCOUNT_URL = "{}/account/create".format(API_URL)

    #OBJECTS
    NEW_ACCOUNT_OBJ = {
    "name": "James C",
    "document": "008",
    "dailyWithdrawLimit": "500",
    "accountType": "100"
    }
    NEW_ACCOUNT_ID = ""


    def test_1_get_accounts(self):
        r = requests.get(TestApplication.ACCOUNT_URL)
        res = r.content
        print(res)
        self.assertEqual(r.status_code, 200)

    @unittest.skip("Skip this.")
    def test_2_create_new_account(self):
        r = requests.post(TestApplication.CREATE_ACCOUNT_URL, json=TestApplication.NEW_ACCOUNT_OBJ)
        data = json.loads(r.content)
        TestApplication.NEW_ACCOUNT_ID = data['accountId']
        self.assertEqual(r.status_code, 200)

 
    NEW_DEPOSIT = {
    "accountId": 14,
    "value": 1000
    }

    def test_3_deposit(self):
        r = requests.post("{}/account/deposit".format(TestApplication.API_URL), json=TestApplication.NEW_DEPOSIT)
        data = json.loads(r.content)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(data['value'], 1000)
