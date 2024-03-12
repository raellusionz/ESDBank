from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import psycopg2
import os

app = Flask(__name__)

# Configure PostgreSQL database URI
POSTGRES_USER = "default"
POSTGRES_PASSWORD = "vHFyts8wa4PK"
POSTGRES_HOST = "ep-shiny-wave-a4w35od7-pooler.us-east-1.aws.neon.tech"
POSTGRES_DB = "verceldb"

# PostgreSQL URI format: postgresql://username:password@host:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class user_accounts(db.Model):
    __tablename__ = 'user_acct_details_db'

    bank_acct_id = db.Column(db.String(20), primary_key=True)
    user_email = db.Column(db.String(100), nullable=False)
    user_fullname = db.Column(db.String(255), nullable=False)
    user_hp = db.Column(db.Integer)


    def __init__(self, bank_acct_id, user_email, user_fullname, user_hp):
        self.bank_acct_id = bank_acct_id
        self.user_email = user_email
        self.user_fullname = user_fullname
        self.user_hp = user_hp


    def json(self):
        return {"bank_acct_id": self.bank_acct_id, "user_email": self.user_email, "user_fullname": self.user_fullname, "user_hp": self.user_hp}

@app.route("/")
def homepage():
    return "Welcome to the homepage of the user_accounts microservice Lab4Proj."

@app.route("/userAccounts")
def get_all():
    user_accounts_list = db.session.scalars(db.select(user_accounts)).all()

    if len(user_accounts_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "user_accounts": [user_account.json() for user_account in user_accounts_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no user accounts."
        }
    ), 404

@app.route("/userAccounts/bank_acct_id/<string:id_num>")
def find_by_bank_acct_id(id_num):
    account = db.session.scalars(
    	db.select(user_accounts).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()

    if account:
        return jsonify(
            {
                "code": 200,
                "data": account.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User account not found."
        }
    ), 404

@app.route("/userAccounts/hp_num/<int:hp_num>")
def find_by_user_hp(hp_num):
    account = db.session.scalars(
    	db.select(user_accounts).filter_by(user_hp=hp_num).
    	limit(1)
        ).first()

    if account:
        return jsonify(
            
            {
                "code": 200,
                "data": account.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User account not found."
        }
    ), 404


@app.route("/userAccounts/user_email/<string:email>")
def find_by_user_email(email):
    account = db.session.scalars(
    	db.select(user_accounts).filter_by(user_email=email).
    	limit(1)
        ).first()


    if account:
        return jsonify(
            
            {
                "code": 200,
                "data": account.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "User account not found."
        }
    ), 404

@app.route("/userAccounts/<string:id_num>", methods=['POST'])
def create_user_account(id_num):
    if (db.session.scalars(
      db.select(user_accounts).filter_by(bank_acct_id=id_num).
      limit(1)
      ).first()
      ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "bank_acct_id": id_num
                },
                "message": "Account already exists."
            }
        ), 400

    data = request.get_json()
    account = user_accounts(id_num, **data)

    try:
        db.session.add(account)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "bank_acct_id": id_num
                },
                "message": "An error occurred creating the account."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": account.json()
        }
    ), 201

if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to user_accounts database ...") 
    app.run(host='0.0.0.0', port=5000, debug=True)