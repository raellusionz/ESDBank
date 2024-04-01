from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import psycopg2
import os
from sqlalchemy import BigInteger, or_

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



if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to group_details database ...") 
    app.run(host='0.0.0.0', port=5010, debug=True)