from operator import and_
#from middleware import validAccountId
from flask import Flask, request, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


# Database

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    document = db.Column(db.String(80), nullable=False)
    #birthDate = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'\t<Person %r>\n' % f"{self.id}: {self.name} - {self.document}"

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Integer, default=0, nullable=False)
    dailyWithdrawLimit = db.Column(db.Integer, nullable=False)
    activeFlag = db.Column(db.Boolean, default=True, nullable=False)
    accountType = db.Column(db.Integer, nullable=False)
    createdDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    personId = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    person= db.relationship('Person', backref=db.backref('account', lazy=True))

    def __repr__(self):
        return '\t<Account %r>\n' % f"{self.id}: {self.balance}(Balance) - {self.dailyWithdrawLimit}(Daily whitdraw Limit) - {self.activeFlag}(Active) - {self.accountType}(Account) - {self.createdDate}(Created) - {self.personId}(personId)"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    transactionDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    accountId = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    account = db.relationship('Account', backref=db.backref('transaction', lazy=True))

    def __repr__(self):
        return '\t<Transaction %r>\n' % f"{self.id}: {self.value}(Value) - {self.transactionDate}(Transaction Date) - {self.accountId}(accountId)"

# Endpoints

@app.route('/account')
def getAccounts():
    allAccounts = Account.query.all()

    output = []
    for account in allAccounts:
        accountData = {"id": account.id, "balance": account.balance, "dailyWithdrawLimit": account.dailyWithdrawLimit, "activeFlag": account.activeFlag, "accountType": account.accountType, "createdDate": account.createdDate, "personId": account.personId}
        output.append(accountData)
    return {"accounts": output}

@app.route('/account/transactions')
def getTransactions():
    allTransactionById = db.session.query(Transaction).\
        filter(Transaction.accountId==request.json['accountId']).\
        filter(Transaction.value<0).\
        filter(Transaction.transactionDate>=datetime.today().date())

    output = []
    for transactionById in allTransactionById:
        transactionById = {"id": transactionById.id, "value": transactionById.value, "transactionDate": transactionById.transactionDate, "accountId": transactionById.accountId}
        output.append(transactionById)
    return {"accounts": output, "date": datetime.today().date()}

@app.route('/account/create', methods=['POST'])
def createNewAccount():
    newPerson = Person(name=request.json['name'], document=request.json['document'])
    db.session.add(newPerson)
    db.session.commit()
    newAccount = Account(dailyWithdrawLimit=request.json['dailyWithdrawLimit'], accountType=request.json['accountType'], personId=newPerson.id)
    db.session.add(newAccount)
    db.session.commit()
    return {"personId": newPerson.id, "accountId": newAccount.id}

@app.route('/account/deposit', methods=['POST'])
def deposit():
    accountById = Account.query.filter_by(id=request.json['accountId']).first()
    
    # Wanabe Middleware
    if accountById is None:
        return Response('The account does not exist.', mimetype='application/json', status=401)
    if accountById.activeFlag == False:
        return Response('The account is currently blocked.', mimetype='application/json', status=402)
    if request.json['value'] <= 0:
        return Response('The amount has to be greater that 0.', mimetype='application/json', status=403)
    
    newTransaction = Transaction(value=request.json['value'],accountId=request.json['accountId'])
    db.session.add(newTransaction)
    db.session.commit()

    accountById.balance += request.json['value']
    db.session.commit()

    return {"transactionId": newTransaction.id, "value": newTransaction.value, "newBalance": accountById.balance}

@app.route('/account/balance')
def getBalance():
    accountById = Account.query.filter_by(id=request.json['accountId']).first()

    # Wanabe Middleware
    if accountById is None:
        return Response('The account does not exist.', mimetype='application/json', status=401)
    if accountById.activeFlag == False:
        return Response('The account is currently blocked.', mimetype='application/json', status=401)

    return {"balance": accountById.balance}

@app.route('/account/withdraw', methods=['POST'])
def withdraw():
    accountById = Account.query.filter_by(id=request.json['accountId']).first()

    # Wanabe Middleware
    if accountById is None:
        return Response('The account does not exist.', mimetype='application/json', status=401)
    if accountById.activeFlag == False:
        return Response('The account is currently blocked.', mimetype='application/json', status=402)
    if request.json['value'] <= 0:
        return Response('The amount has to be greater that 0.', mimetype='application/json', status=403)
    todayStatmentsById = db.session.query(func.sum(Transaction.value)).\
        filter(Transaction.accountId==request.json['accountId']).\
        filter(Transaction.value<0).\
        filter(Transaction.transactionDate>=datetime.today().date()).first()
    if todayStatmentsById[0] is not None:
        if (accountById.dailyWithdrawLimit <= abs(todayStatmentsById[0])):
            return Response('The daily widthraw limit has been reach.', mimetype='application/json', status=405)

    newTransaction = Transaction(value=-abs(request.json['value']), accountId=request.json['accountId'])
    db.session.add(newTransaction)
    db.session.commit()

    accountById.balance -= request.json['value']
    db.session.commit()

    return {"transactionId": newTransaction.id, "value": newTransaction.value, "newBalance": accountById.balance}

@app.route('/account/block', methods=['PUT'])
def block():
    accountById = Account.query.filter_by(id=request.json['accountId']).first()
    accountById.activeFlag = False
    db.session.commit()

    return {"message": f"Account {accountById.id} has been blocked"}

@app.route('/account/statment')
def getStatments():
    allStatmentsById = Transaction.query.filter_by(accountId=request.json['accountId'])

    output = []
    for statment in allStatmentsById:
        statmentData = {"id": statment.id, "value": statment.value, "transactionDate": statment.transactionDate, "accountId": statment.accountId}
        output.append(statmentData)
    return {"statements": output}

@app.route('/account/statment/period')
def getStatmentByPeriod():
    allStatmentsById = Transaction.query.filter(and_(Transaction.accountId==request.json['accountId'], Transaction.transactionDate.between(datetime.strptime(request.json['from'], '%d/%m/%Y'), datetime.strptime(request.json['to'], '%d/%m/%Y'))))
    
    output = []
    for statment in allStatmentsById:
        statmentData = {"id": statment.id, "value": statment.value, "transactionDate": statment.transactionDate, "accountId": statment.accountId}
        output.append(statmentData)
    return {"statements": output}