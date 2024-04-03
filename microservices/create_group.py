from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

from invokes import invoke_http

import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)

user_accounts_URL = "http://127.0.0.1:5000/userAccounts/hp_num/"
#bank_accounts_URL = "http://127.0.0.1:5001/bankAccounts/transferral/"
#transaction_history_URL = "http://127.0.0.1:5002/transaction_history"
group_details_URL = "http://127.0.0.1:5010/group_details"

# These exchanges may need to be changed specific to this MS
# exchangename = amqp_connection.secrets['exchangename'] #transfer_funds_topic
# exchangetype = amqp_connection.secrets['exchangetype'] #topic 
exchangename = "transfer_funds_topic" #transfer_funds_topic
exchangetype = "topic" #topic 

#create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

@app.route("/")
def homepage():
    return "Welcome to the homepage of the create_group microservice Lab4Proj."

@app.route("/create_group", methods=['POST'])
def create_group():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            details = request.get_json()
            print("\nReceived a create group request in JSON:", details)

            # do the actual work
            # 1. Send group details from UI { [phoneNum1, phoneNum2, etc.], currUserBAN, currUserFullname, curUserPhoneNum, currUserEmail, groupName }
            result = processCreateGroup(details)
            print('\n------------------------')
            print('\nresult: ', result)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "create_group.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processCreateGroup(details):
    curr_user_ban = details["curr_user_ban"]
    curr_user_fullname = details['curr_user_fullname']
    curr_user_hp = details["curr_user_hp"]
    curr_user_email = details['curr_user_email']

    group_name = details['group_name']
    phone_num_list = details['phone_num_list']

    # 2. Send the list of phone numbers {[phoneNum1, phoneNum2, etc.]} to user_accounts to get details
    # Invoke the user_accounts microservice
    print('\n-----Invoking user_accounts microservice-----')
    member_details_dict = {}
    count = 0
    for num in phone_num_list:
        print(num, type(num))
        user_accounts_result = invoke_http(user_accounts_URL+f"{num}", method='GET')
        member_details_dict[count] = user_accounts_result
        count += 1
        
        print(f'user_accounts_result {num+1}:', user_accounts_result)
        code = user_accounts_result["code"]
        message = json.dumps(user_accounts_result)

        if code not in range(200, 300):

            print('\n\n-----Publishing the (user_accounts lookup error) message with routing_key=user_accounts.error-----')
            channel.basic_publish(exchange=exchangename, routing_key="user_accounts.error", 
                body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
            # make message persistent within the matching queues until it is received by some receiver 
            # (the matching queues have to exist and be durable and bound to the exchange)


            # - reply from the invocation is not used; 
            # continue even if this invocation fails
            print("\nUser_accounts MS status ({:d}) published to the RabbitMQ Exchange:".format(
                code), user_accounts_result)


            # 5. Return error
            return {
                "code": 500,
                "data": {"user_accounts_result": user_accounts_result},
                "message": "User_accounts lookup failure sent for error handling."
            }
        
        else:
            # 4. Record new user_accounts lookup activity
            print('\n\n-----Publishing the (user_accounts lookup details) message with routing_key=user_accounts.details-----')        
            channel.basic_publish(exchange=exchangename, routing_key="user_accounts.details", 
                body=message)
            
        print("\nDatabase phone number lookup request published to RabbitMQ Exchange.\n")
        # - reply from the invocation is not used;
        # continue even if this invocation fails

    # should be in the format : { 
    #                             0: {                                            1: {
    #                                  "code": 200,                                    "code": 200,
    #                                  "data": {                                       "data": {
    #                                     "bank_acct_id": "111111111111",                 "bank_acct_id": "000000000000",
    #                                     "user_email": "user1@gmail.com",                "user_email": "abc@gmail.com",
    #                                     "user_fullname": "John Tan Lim",                "user_fullname": "Paul Wang Tham",
    #                                     "user_hp": 12345678                             "user_hp": 98765432
    #                                          }                                                    }
    #                                 },                                                }, etc.
    #                             }

    #add curr_user details into dict    
    member_details_dict[-1] = {"data": 
                                    {                         
                                    "bank_acct_id": curr_user_ban,
                                    "user_email": details['curr_user_email'],
                                    "user_fullname": curr_user_fullname,
                                    "user_hp": curr_user_hp
                                    }
                                }

    print('member_details_result:', member_details_dict)


    # 5. Send retrieved member_details to group_details microservice
    print('\n\n-----Invoking group_details microservice-----')

    group_details_full = {
                            "members": member_details_dict,
                            "group_name": group_name
                        }

    group_details_result = invoke_http(group_details_URL, method="POST", json=group_details_full)
    message = json.dumps(group_details_result)
    print('group_details_result:', group_details_result)


    # Check the transfer request result; if a failure, send it to the error microservice.
    code = group_details_result["code"]
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Publishing the (group_details error) message with routing_key=group_details.error-----')
        message = json.dumps(group_details_result)
        channel.basic_publish(exchange=exchangename, routing_key="group_details.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nGroup_details MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), group_details_result)


        # 7. Return error
        return {
            "code": 400,
            "data": {"group_details_result": group_details_result},
            "message": "Group_details group creation sent for error handling."
        }
    
    else:
        # 4. Record group_details
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (group_details transfer details) message with routing_key=group_details.details-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        channel.basic_publish(exchange=exchangename, routing_key="group_details.details", 
            body=message)
        
    print("\nGroup creation request published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 9. Send the relevant info {senderFullname, recipientFullname, senderEmail, recipientEmail} to notification microservice
    # Invoke the notification microservice
    print('\n\n-----Invoking notification microservice-----')

    print('\n\n-----Publishing the (notification details) message with routing_key=notification.details-----')
    for i in range(0,len(member_details_dict)-1,1):
        data = {
            "data": {
                "inviter": curr_user_fullname,
                "invitee": member_details_dict[i]["data"]["user_fullname"],
                "email": member_details_dict[i]["data"]["user_email"],
                "group_name": group_name
                },
            "notification_type": "create_group"
            }    
        message = json.dumps(data)
        channel.basic_publish(exchange=exchangename, routing_key="notification.details", body=message)

    # 10. Return successful group creation results
    return {
        "code": 201,
        "data": {
            "group_details_result": group_details_result,
        }

    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) +
          " for group creation...")
    app.run(host="0.0.0.0", port=5200, debug=True)