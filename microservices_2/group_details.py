from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import psycopg2
import os
from sqlalchemy import BigInteger, or_, ForeignKey

app = Flask(__name__)

# Configure PostgreSQL database URI
POSTGRES_USER = "default"
POSTGRES_PASSWORD = "NDSa5jc6eqAT"
POSTGRES_HOST = "ep-crimson-sky-a1j2iovr-pooler.ap-southeast-1.aws.neon.tech"
POSTGRES_DB = "verceldb"

# PostgreSQL URI format: postgresql://username:password@host:port/database_name
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class group_details(db.Model):
    __tablename__ = 'sp_group_details_db'

    group_id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(255), nullable=False)

    def __init__(self, group_name):
        self.group_name = group_name

    def json(self):
        return {
            "group_id": self.group_id,
            "group_name": self.group_name,
        }

class members(db.Model):
    __tablename__ = 'sp_members_db'

    group_id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    member_ban = db.Column(db.String(20), primary_key=True)
    group_name = db.Column(db.String(255), nullable=False)
    member_hp = db.Column(db.Integer, nullable=False)
    member_fullname = db.Column(db.String(255), nullable=False)
    member_email = db.Column(db.String(255))


    def __init__(self, group_id, member_ban, group_name, member_hp, member_fullname, member_email):
        self.group_id = group_id
        self.member_ban = member_ban
        self.group_name = group_name
        self.member_hp = member_hp
        self.member_fullname = member_fullname
        self.member_email = member_email


    def json(self):
        return {
            "group_id": self.group_id,
            "member_ban": self.member_ban,
            "group_name": self.group_name,
            "member_hp": self.member_hp,
            "member_fullname": self.member_fullname,
            "member_email": self.member_email,
        }
    
class split_requests(db.Model):
    __tablename__ = 'sp_split_requests'

    req_id = db.Column(BigInteger, primary_key=True, autoincrement = True)
    group_id = db.Column(BigInteger, ForeignKey('sp_group_details_db.group_id'))
    total_req_amount = db.Column(db.DECIMAL(15,2), nullable=False)
    requester_phone_num = db.Column(db.Integer, nullable=False)
    req_date_time = db.Column(db.String(100))


    def __init__(self, group_id, total_req_amount, requester_phone_num, req_date_time):
        self.group_id = group_id
        self.total_req_amount = total_req_amount
        self.requester_phone_num = requester_phone_num
        self.req_date_time =req_date_time

    def json(self):
        return {
            "req_id": self.req_id,
            "group_id": self.group_id,
            "total_req_amount": float(self.total_req_amount),
            "requester_phone_num": self.requester_phone_num,
            "req_date_time": self.req_date_time
        }

class requested_users(db.Model):
    __tablename__ = 'sp_requested_user'

    req_id = db.Column(BigInteger, ForeignKey('sp_split_requests.req_id'))
    userBAN = db.Column(db.String(20), primary_key=True)
    indiv_req_amount = db.Column(db.DECIMAL(15,2), nullable=False)
    status = db.Column(db.String(10))
    resp_date_time = db.Column(db.String(100))


    def __init__(self, req_id, userBAN, indiv_req_amount, status, resp_date_time):
        self.req_id = req_id
        self.userBAN = userBAN
        self.indiv_req_amount = indiv_req_amount
        self.status = status
        self.resp_date_time =resp_date_time

    def json(self):
        return {
            "req_id": self.req_id,
            "user_ban": self.userBAN,
            "indiv_req_amount": float(self.indiv_req_amount),
            "status": self.status,
            "resp_date_time": self.resp_date_time
        }

@app.route("/")
def homepage():
    return "Welcome to the homepage of the group_details microservice Lab4Proj."

@app.route("/groupDetails")
def get_all_groups():
    group_details_list = db.session.scalars(db.select(group_details)).all()

    if len(group_details_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "group_details": [group.json() for group in group_details_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no groups in the database."
        }
    ), 404

@app.route("/members")
def get_all_members():
    member_details_list = db.session.scalars(db.select(members)).all()

    if len(member_details_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "members_details": [member.json() for member in member_details_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no members in any groups."
        }
    ), 404

@app.route("/splitRequests")
def get_all_split_requests():
    split_requests_list = db.session.scalars(db.select(split_requests)).all()

    if len(split_requests_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "split_requests": [split_request.json() for split_request in split_requests_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no split requests in any groups."
        }
    ), 404

@app.route("/requestedMembers")
def get_all_requested_members():
    requested_members_list = db.session.scalars(db.select(requested_users)).all()

    if len(requested_members_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "requested_member": [requested_member.json() for requested_member in requested_members_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no requested members in any groups."
        }
    ), 404

@app.route("/group_details", methods=['POST'])
def insertGroupDetails():
    # Check if the submitted details contains valid JSON
    group_details = None
    if request.is_json:
        group_details = request.get_json()
        result = processGroupDetails(group_details)
        return result#, result["code"]
    else:
        data = request.get_data()
        print("Received invalid group details:")
        print(data)
        return jsonify({"code": 400,
                        # make the data string as we dunno what could be the actual format
                        "data": str(data),
                        "message": "Group details should be in JSON."}), 400  # Bad Request input


def processGroupDetails(details):
    print("Processing group details:")
    print(details)
    member_details_dict = details["members"]
    print(member_details_dict)
    group_name = details["group_name"]

    print()  # print a new line feed as a separator

    # create new group record
    new_group = group_details(group_name)
    try:
        db.session.add(new_group)
        db.session.commit()

    except:
        return  {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred logging the group name."
                }
    
    # retrieve group_id
    created_group_id = new_group.group_id
    
    # store members in list
    created_members_list = []

    # create member records using created group_id
    for i in range(-1, len(member_details_dict)-1, 1):
        member_ban = member_details_dict[str(i)]["data"]["bank_acct_id"]
        member_hp = member_details_dict[str(i)]["data"]["user_hp"]
        member_fullname = member_details_dict[str(i)]["data"]["user_fullname"]
        member_email = member_details_dict[str(i)]["data"]["user_email"]   

        # create and add member record
        new_member = members(group_id=created_group_id,
                                member_ban=member_ban,
                                group_name=group_name,
                                member_hp=member_hp,
                                member_fullname=member_fullname,
                                member_email=member_email)
        try:
            db.session.add(new_member)    
            db.session.commit()
            created_members_list.append(new_member)

        except:
            return  {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred logging the group members."
                }


    return  {
            "code": 201,
            "message": "Group successfully created and members successfully added.",
            "data": {"created_group": new_group.json(), "added_members": [member.json() for member in created_members_list]}
            }



@app.route("/split_payment_details", methods=['POST'])
def insertSplitPaymentDetails():
    # Check if the submitted details contains valid JSON
    split_payment_details = None
    if request.is_json:
        split_payment_details = request.get_json()
        result = processSplitPaymentDetails(split_payment_details)
        return result#, result["code"]
    else:
        data = request.get_data()
        print("Received invalid split payment details:")
        print(data)
        return jsonify({"code": 400,
                        # make the data string as we dunno what could be the actual format
                        "data": str(data),
                        "message": "Split payment details should be in JSON."}), 400  # Bad Request input


def processSplitPaymentDetails(details):
    print("Processing split payment details:")
    print(details)
    amount_to_split = details["data"]["req_amount"]
    requester_phone_num = details["data"]["requester_phone_num"]
    group_id = details["data"]["group_id"]



    print()  # print a new line feed as a separator

    # create new group record
    new_request = split_requests()
    try:
        db.session.add(new_group)
        db.session.commit()

    except:
        return  {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred logging the group name."
                }
    
    # retrieve group_id
    created_group_id = new_group.group_id
    
    # store members in list
    created_members_list = []

    # create member records using created group_id
    for i in range(-1, len(member_details_dict)-1, 1):
        member_ban = member_details_dict[str(i)]["data"]["bank_acct_id"]
        member_hp = member_details_dict[str(i)]["data"]["user_hp"]
        member_fullname = member_details_dict[str(i)]["data"]["user_fullname"]
        member_email = member_details_dict[str(i)]["data"]["user_email"]   

        # create and add member record
        new_member = members(group_id=created_group_id,
                                member_ban=member_ban,
                                group_name=group_name,
                                member_hp=member_hp,
                                member_fullname=member_fullname,
                                member_email=member_email)
        try:
            db.session.add(new_member)    
            db.session.commit()
            created_members_list.append(new_member)

        except:
            return  {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred logging the group members."
                }


    return  {
            "code": 201,
            "message": "Group successfully created and members successfully added.",
            "data": {"created_group": new_group.json(), "added_members": [member.json() for member in created_members_list]}
            }


if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to group_details database ...") 
    app.run(host='0.0.0.0', port=5010, debug=True)