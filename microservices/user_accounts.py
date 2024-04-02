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

class user_preference_logs(db.Model):
    __tablename__ = 'user_prefers_table'

    bank_acct_id = db.Column(db.String(20), primary_key=True)
    saving_goal_percentage = db.Column(db.DECIMAL(15,2))
    necessity_expenditure_percentage = db.Column(db.DECIMAL(15,2))
    fund_transfer = db.Column(db.DECIMAL(15,2))
    necessities = db.Column(db.DECIMAL(15,2))
    transportation = db.Column(db.DECIMAL(15,2))
    f_b = db.Column(db.DECIMAL(15,2))
    shop_entertain = db.Column(db.DECIMAL(15,2))
    others = db.Column(db.DECIMAL(15,2))

    def __init__(self, bank_acct_id, saving_goal_percentage, necessity_expenditure_percentage,fund_transfer,necessities, transportation, f_b, shop_entertain, others):
        self.bank_acct_id = bank_acct_id
        self.saving_goal_percentage = saving_goal_percentage
        self.necessity_expenditure_percentage = necessity_expenditure_percentage
        self.fund_transfer = fund_transfer
        self.necessities = necessities
        self.transportation = transportation
        self.f_b = f_b
        self.shop_entertain = shop_entertain
        self.others = others


    def json(self):
        return {
            "bank_acct_id": self.bank_acct_id, 
            "saving_goal_percentage": self.saving_goal_percentage,
            "necessity_expenditure_percentage": self.necessity_expenditure_percentage,
            "fund_transfer": self.fund_transfer,
            "necessities": self.necessities,
            "transportation": self.transportation,
            "f_b" : self.f_b,
            "shop_entertain" : self.shop_entertain,
            "others": self.others}

@app.route("/")
def homepage():
    return "Welcome to the homepage of the user_accounts microservice Lab4Proj."

@app.route("/userAccounts")
def get_all_userAccounts():
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

# Get the whole userPreference table

@app.route("/userPreference")
def get_all_userPreference():
    user_preference_list = db.session.scalars(db.select(user_preference_logs)).all()

    if len(user_preference_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "User Preference": [user_preference.json() for user_preference in user_preference_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are No User Preference Available."
        }
    ), 404


#retreiving user saving goals percent

@app.route("/userPreference/user_saving_goal/<string:id_num>")
def get_saving_percent(id_num):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        saving_goal_percentage = account.json()["saving_goal_percentage"]
        return jsonify(    
            {
                "code": 200,
                "data": {
                    "saving_goal_percent": saving_goal_percentage
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#retreiving user necessity expenditure percent

@app.route("/userPreference/user_expenditure/<string:id_num>")
def get_expenditure_percent(id_num):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        necessity_expenditure_percentage = account.json()["necessity_expenditure_percentage"]
        fund_transfer = account.json()["fund_transfer"]
        necessities = account.json()["necessities"]
        transportation = account.json()["transportation"]
        f_b = account.json()["f_b"]
        shop_entertain = account.json()["shop_entertain"]
        others = account.json()["others"]
       
        return jsonify(    
            {
                "code": 200,
                "data": {
                    "expanditure_target_percent": necessity_expenditure_percentage,
                    "breakdown": {
                        "Fund Transfer": fund_transfer,
                        "Necessities": necessities,
                        "Transportation": transportation,
                        "Food & Drink": f_b,
                        "Shopping & Entertainment": shop_entertain,
                        "Others": others
                    }
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#Updating user saving goals percent
@app.route("/userPreference/update_saving_goal/<string:id_num>/<float:saving_percent>",methods=['PUT'])
def update_saving_goal(id_num,saving_percent):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    
    if account:
        saving_goal_percentage = account["saving_goal_percentage"]
        necessity_expenditure_percentage = account.json()["necessity_expenditure_percentage"]
        total = saving_percent + necessity_expenditure_percentage
        
        if (saving_goal_percentage != 0) and (necessity_expenditure_percentage !=0):
            if(total<=100):
                account.saving_goal_percentage = saving_percent
                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "message": "Saving Goal Updated Successfully.",
                        "data": 
                            {
                                "account": account.json()
                            }
                    }
                )
            else:
                return jsonify(
                    {
                        "code": 403,
                        "message": "Please re-assign your saving goals, value is greater than your expenditure goals. Ensure it totals up to 100%"
                    }
                )  
        else:
            return jsonify(
                {
                    "code": 403,
                    "message": "You have not set a goal. Please create a new goal!"
                }
            )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#Updating necessity expenditure percent
@app.route("/userPreference/update_expenditure_target/<string:id_num>/<float:fund_transfer>/<float:necessities>/<float:transportation>/<float:f_b>/<float:shop_entertain>/<float:others>",methods=['PUT'])
def update_expenditure_target(id_num,fund_transfer,necessities,transportation,f_b,shop_entertain,others):

    total_expenditure_percent = fund_transfer + necessities + transportation + f_b + shop_entertain + others
        
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        saving_goal_percentage = account["saving_goal_percentage"]
        necessity_expenditure_percentage = account["necessity_expenditure_percentage"]
        if (saving_goal_percentage != 0) and (necessity_expenditure_percentage !=0):
            if(total_expenditure_percent<=100):
                account.fund_transfer = fund_transfer
                account.necessities = necessities
                account.transportation = transportation
                account.f_b = f_b
                account.shop_entertain = shop_entertain
                account.others = others
                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "message": "Expenditure Target Updated Successfully.",
                        "data": 
                            {
                                "account": account.json()
                            }
                    }
                )
            else:
                return jsonify(
                    {
                        "code": 403,
                        "message": "Please re-assign your expenditure goals, value is greater than your expenditure goals. Ensure it totals up to 100%"
                    }
                )
        else:
            return jsonify(
                {
                    "code": 403,
                    "message": "You have not set a goal. Please create a new goal!"
                }
            )
    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#Updating a complete new user saving goals percent
@app.route("/userPreference/update_new_user_preference_goal/<string:id_num>/<float:saving_percent>/<float:fund_transfer>/<float:necessities>/<float:transportation>/<float:f_b>/<float:shop_entertain>/<float:others>",methods=['PUT'])

def update_new_user_preference_goal(id_num,saving_percent,fund_transfer,necessities,transportation,f_b,shop_entertain,others):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    
    if account:
        saving_goal_percentage = account["saving_goal_percentage"]
        necessity_expenditure_percentage = account.json()["necessity_expenditure_percentage"]
        
        if (saving_goal_percentage != 0) and (necessity_expenditure_percentage !=0):
            total_expenditure_percent = fund_transfer + necessities + transportation + f_b + shop_entertain + others
            total = saving_percent + total_expenditure_percent
            if (total <= 100): #less or equal to 100
                account.saving_goal_percentage = saving_percent
                account.fund_transfer = fund_transfer
                account.necessities = necessities
                account.transportation = transportation
                account.f_b = f_b
                account.shop_entertain = shop_entertain
                account.others = others
                db.session.commit()
                return jsonify(
                    {
                        "code": 200,
                        "message": "New Saving Goal Target Updated Successfully.",
                        "data": 
                            {
                                "account": account.json()
                            }
                    }
                )
            else:
                return jsonify(
                    {
                        "code": 403,
                        "message": "Please re-assign your saving and expenditure goals. Ensure it totals up to 100%"
                    }
                )
        else:
            return jsonify(
                {
                    "code": 403,
                    "message": "You have not set a goal. Please create a new goal!"
                }
            )

    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404


#Create a complete new user saving goals percent
@app.route("/userPreference/create_new_user_preference_goal/<string:id_num>/<float:saving_percent>/<float:fund_transfer>/<float:necessities>/<float:transportation>/<float:f_b>/<float:shop_entertain>/<float:others>",methods=['PUT'])

def create_new_user_preference_goal(id_num,saving_percent,fund_transfer,necessities,transportation,f_b,shop_entertain,others):
    account = db.session.scalars(
    	db.select(user_preference_logs).filter_by(bank_acct_id=id_num).
    	limit(1)
        ).first()
    if account:
        saving_goal_percentage = account["saving_goal_percentage"]
        necessity_expenditure_percentage = account.json()["necessity_expenditure_percentage"]
        
        if (saving_goal_percentage == 0) and (necessity_expenditure_percentage ==0):
            total_expenditure_percent = fund_transfer + necessities + transportation + f_b + shop_entertain + others
            total = saving_percent + total_expenditure_percent
            if (total <= 100): #less or equal to 100
                account.saving_goal_percentage = saving_percent
                account.fund_transfer = fund_transfer
                account.necessities = necessities
                account.transportation = transportation
                account.f_b = f_b
                account.shop_entertain = shop_entertain
                account.others = others
                db.session.commit()
                return jsonify(
                    {
                        "code": 201,
                        "message": "New Saving Goal Target Created Successfully.",
                        "data": 
                            {
                                "account": account.json()
                            }
                    }
                )
            else:
                return jsonify(
                    {
                        "code": 403,
                        "message": "Please re-assign your saving and expenditure goals. Ensure it totals up to 100%"
                    }
                )
        else:
            return jsonify(
                {
                    "code": 403,
                    "message": "You already have set your goals. Update your goals instead!"
                }
            )

    return jsonify(
        {
            "code": 404,
            "message": "Bank account not found."
        }
    ), 404

if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to user_accounts database ...") 
    app.run(host='0.0.0.0', port=5000, debug=True)