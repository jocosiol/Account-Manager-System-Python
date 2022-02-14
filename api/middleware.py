# Middlewares

# 1- isMaxDalyWithdraw
# 2- validAccountId
# 3- valisTransactionValue
# 4- validateBody

from functools import wraps
from flask import Response, request
from application import Account

def valid_account_id(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        accountById = Account.query.filter_by(id=request.json['accountId']).first()
        if accountById.activeFlag == True:
            return func(*args, **kwargs)
        return Response('The account is currently blocked.', mimetype='application/json', status=401)
    return decorated_func


