from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import psycopg2
import os
from sqlalchemy import BigInteger, and_, ForeignKey, PrimaryKeyConstraint
from datetime import datetime

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
    group_id = db.Column(db.Integer, ForeignKey('sp_group_details_db.group_id'))
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

    req_id = db.Column(db.Integer, ForeignKey('sp_split_requests.req_id'))
    userban = db.Column(db.String(20))
    indiv_req_amount = db.Column(db.DECIMAL(15,2), nullable=False)
    status = db.Column(db.String(10))
    resp_date_time = db.Column(db.String(100))

    __table_args__ = (
        PrimaryKeyConstraint('req_id', 'userban'),
    )

    def __init__(self, req_id, userban, indiv_req_amount, status, resp_date_time):
        self.req_id = req_id
        self.userban = userban
        self.indiv_req_amount = indiv_req_amount
        self.status = status
        self.resp_date_time =resp_date_time

    def json(self):
        return {
            "req_id": self.req_id,
            "user_ban": self.userban,
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

# get the groups that a member is in using their BAN
@app.route("/members/bank_acct_id/<string:user_ban>")
def get_member_groups_by_BAN(user_ban):
    groups_member_is_in_list = db.session.scalars(
        db.select(members).filter_by(member_ban=user_ban)
        ).all()

    if len(groups_member_is_in_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "groups_member_is_in": [group.json() for group in groups_member_is_in_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "The user does not belong to any groups."
        }
    ), 404

# get each member of a group based on a given group ID number
@app.route("/members/group_id/<int:group_id_num>")
def get_members_by_group_id(group_id_num):
    members_of_group_list = db.session.scalars(
        db.select(members).filter_by(group_id=group_id_num)
        ).all()

    if len(members_of_group_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "groups_members": [member.json() for member in members_of_group_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "The group does not exist."
        }
    ), 404

# get each request in a group based off given group ID number, then for each request ID get the associated members who have to pay money
@app.route("/requestedMembers/group_id/<int:group_id_num>")
def get_requested_members_by_group_id(group_id_num):
    split_requests_list = db.session.scalars(
        db.select(split_requests).filter_by(group_id=group_id_num)
        ).all()

    if len(split_requests_list) == 0:
        return jsonify(
            {
                "code": 404,
                "message": "There are no split requests for this group."
            }
        )
    
    data = {}
    for request in split_requests_list:
        request_req_id = request.req_id
        requested_members_list = db.session.scalars(
            db.select(requested_users).filter_by(req_id=request_req_id)
            ).all()
        data[request_req_id] = [member.json() for member in requested_members_list]

    return jsonify(
            {
                "code": 200,
                "data": {
                    "requests_by_id": data
                }
            }
        )

# get the split requests of the user with the given BAN
@app.route("/requestedMembers/user_ban/<string:user_ban>")
def get_requested_members_by_userBAN(user_ban):
    requests_to_user_list = db.session.scalars(
        db.select(requested_users).filter_by(userban=user_ban)
        ).all()

    if len(requests_to_user_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "requests_to_this_user": [request.json() for request in requests_to_user_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "The user does not exist."
        }
    ), 404

# get the split requests made by the user with the given phone number, and the associated members who need to pay
@app.route("/splitRequests/requestedMembers/user_hp/<int:user_hp>")
def get_split_requests_of_user_by_user_hp(user_hp):
    split_requests_made_by_user_list = db.session.scalars(
        db.select(split_requests).filter_by(requester_phone_num=user_hp)
        ).all()

    if len(split_requests_made_by_user_list) == 0:
        return jsonify(
            {
                "code": 404,
                "message": "This user has not made any split requests."
            }
        )
    
    data = {}
    for request in split_requests_made_by_user_list:
        request_req_id = request.req_id
        requested_members_list = db.session.scalars(
            db.select(requested_users).filter_by(req_id=request_req_id)
            ).all()
        data[request_req_id] = [member.json() for member in requested_members_list]

    return jsonify(
            {
                "code": 200,
                "data": {
                    "split_requests_made_by_user": [request.json() for request in split_requests_made_by_user_list],
                    "requested_users_by_req_id": data
                }
            }
        )



# get requested_member where group_id == given_group_id, requested_member.userBAN==currUserBAN and status==pending, with names of requester and payer
@app.route("/splitRequests/pendingRequests/user_details/<string:user_ban>/<int:user_hp>/<int:group_id>")
def get_pending_requests_to_user_by_group_id(user_ban, user_hp, group_id):

    # retrieve list of split_requests in this group that was not made by this user
    requests_to_user_list = db.session.scalars(
                                        db.select(split_requests)
                                            .filter(
                                                and_(split_requests.group_id==group_id,
                                                    split_requests.requester_phone_num!=user_hp))).all()

    if len(requests_to_user_list) == 0:
        return jsonify(
            {
                "code": 404,
                "message": "The other users in this group have not made any split requests."
            }
        )
    

    pending_requests_to_user_details = {}
    for request in requests_to_user_list:
        request_req_id = request.req_id
        pending_request = db.session.scalars(
                            db.select(requested_users).filter(
                                and_(requested_users.req_id==request_req_id,
                                     requested_users.userban==user_ban,
                                     requested_users.status=="pending")).limit(1)).first()
        if pending_request != None:
            ret_payment_amount = pending_request.indiv_req_amount
        requester_phone_num = request.requester_phone_num

        requester_details = db.session.scalars(
                            db.select(members).filter_by(member_hp=requester_phone_num).limit(1)
                            ).first()

        requester_name = requester_details.member_fullname

        pending_requests_to_user_details[request_req_id] = {
                                                            "requester_name": requester_name,
                                                            "requester_hp": requester_phone_num,
                                                            "amount_to_pay": ret_payment_amount
                                                            }

    return jsonify(
            {
                "code": 200,
                "data": {
                    "pending_requests_to_user_by_id": pending_requests_to_user_details
                }
            }
        )

# # get requests where user asked for money and the members have paid
# @app.route("/splitRequests/acceptedRequests/user_phone_num/<int:user_hp>/<int:group_id>")
# def get_users_accepted_requests_by_group_id(user_hp, group_id):

#     # retrieve list of split_requests in this group that was not made by this user
#     users_requests_list = db.session.scalars(
#                                         db.select(split_requests)
#                                             .filter(
#                                                 and_(split_requests.group_id==group_id,
#                                                     split_requests.requester_phone_num==user_hp))).all()

#     if len(users_requests_list) == 0:
#         return jsonify(
#             {
#                 "code": 404,
#                 "message": "The user has not made any requests."
#             }
#         )
    

#     users_accepted_split_requests_details = {}
#     for request in users_requests_list:
#         request_req_id = request.req_id
#         accepted_requests_list = db.session.scalars(
#                             db.select(requested_users).filter(
#                                 and_(requested_users.req_id==request_req_id,
#                                      requested_users.status=="accepted"))).all()
        
#         if accepted_requests_list:
#             for accepted_request_user in accepted_requests_list:
#                 print(accepted_request_user)
#                 indiv_payment = accepted_request_user.indiv_req_amount
#                 accepted_request_user_ban = accepted_request_user.userban
#                 accepted_request_user_details = db.session.scalars(
#                                                 db.select(members).filter_by(userban=accepted_request_user_ban).limit(1)
#                                                 ).first()
            
#                 if request_req_id in users_accepted_split_requests_details:
#                     users_accepted_split_requests_details[request_req_id].append({
#                                                             "name_of_payer": accepted_request_user_details.member_fullname,
#                                                             "amount_to_pay": indiv_payment
#                                                             })
#                 else:
#                     users_accepted_split_requests_details[request_req_id] = [{
#                                                             "name_of_payer": accepted_request_user_details.member_fullname,
#                                                             "amount_to_pay": indiv_payment
#                                                             }]

#     return jsonify(
#             {
#                 "code": 200,
#                 "data": {
#                     "accepted_requests_to_user_by_id": users_accepted_split_requests_details
#                 }
#             }
#         )

# add new group and the members into database
@app.route("/group_details", methods=['POST'])
def insertGroupDetails(): 
    # Check if the submitted details contains valid JSON
    group_details = None
    if request.is_json:
        group_details = request.get_json()
        result = processGroupDetails(group_details)
        return result, result["code"]
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
    print(created_group_id)
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

    print(created_members_list)

    return  {
            "code": 201,
            "message": "Group successfully created and members successfully added.",
            "data": {"created_group": new_group.json(), "added_members": [member.json() for member in created_members_list]}
            }


# add new split_payment request details into the database
@app.route("/split_payment_details", methods=['POST'])
def insertSplitPaymentDetails():
    # Check if the submitted details contains valid JSON
    split_payment_details = None
    if request.is_json:
        split_payment_details = request.get_json()
        result = processSplitPaymentDetails(split_payment_details)
        return result, result["code"]
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
    amount_to_split = details["req_amount"]
    requester_phone_num = details["requester_phone_num"]
    group_id = details["group_id"]
    req_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print()  # print a new line feed as a separator

    # create new group record
    new_request = split_requests(group_id, amount_to_split, requester_phone_num, req_datetime)
    try:
        db.session.add(new_request)
        db.session.commit()

    except:
        return  {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred logging the split_request."
                }

    # retrieve list of group members in this specific group_id
    requested_members_list = db.session.scalars(db.select(members)
                                                .filter(
                                                    and_(members.group_id == group_id,
                                                         members.member_hp != requester_phone_num))).all()

    # retrieve req_id
    created_req_id = new_request.req_id

    # calculate the split amount to pay
    indiv_amount = amount_to_split/(len(requested_members_list))

    # store created_requested_member_list
    created_requested_member_list = []

    # create requested_member records using submitted group_id
    for requested_member in requested_members_list:
        if requested_member.member_hp == requester_phone_num:
            pass
        else:
            member_ban = requested_member.member_ban

            # create and add member record
            new_requested_member = requested_users(req_id=created_req_id,
                                                    userban=member_ban,
                                                    indiv_req_amount=indiv_amount,
                                                    status="pending",
                                                    resp_date_time=None
                                                    )

            try:
                db.session.add(new_requested_member)   
                db.session.commit()
                created_requested_member_list.append(new_requested_member)

            except Exception as e:
                # Log the error
                print(f"Error occurred while creating requested member: {e}")


    if created_requested_member_list:
        return {
            "code": 201,
            "message": "Split_request successfully created and requested_members successfully stored.",
            "data": {
                "created_split_request": new_request.json(),
                "created_requested_members": [requested_member.json() for requested_member in created_requested_member_list],
                "requested_members_details": [member.json() for member in requested_members_list],
                "request_amount": indiv_amount,
                "datetime": req_datetime
            }
        }

    return {
        "code": 500,
        "data": request.get_json(),
        "message": f"An error occurred logging the split_request or requested_members for this split request id:{created_req_id}."
    }

# To adjust the reply status of a requested_member log in the database by taking in the replier BAN, req_id and the reply ("accept" or "decline")
@app.route("/requestedMembers/updateRequest/<string:user_ban>/<int:req_id>/<string:reply>", methods=['PUT'])
def updateRequestStatus(user_ban, req_id, reply):
    # retrieve the specific request to be updated
    request_to_update = db.session.scalars(
    	db.select(requested_users).filter(
            and_(requested_users.userban==user_ban,
                 requested_users.req_id==req_id)).limit(1)).first()

    if request_to_update:
        request_to_update.status = reply
        time_of_reply = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_to_update.resp_date_time = time_of_reply
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Request status successfully updated with reply and datetime.",
                "data": 
                    {
                        "timeOfReply": time_of_reply,
                        "reply": reply,
                        "updatedRequest": request_to_update.json()
                    }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "The specific request is not found."
        }
    ), 404



if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    # Changed to line below
    print("This is flask for " + os.path.basename(__file__) +
          ": connecting to group_details database ...") 
    app.run(host='0.0.0.0', port=5010, debug=True)