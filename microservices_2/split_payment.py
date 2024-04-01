from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

import requests
from invokes import invoke_http

import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)

group_details_URL = "http://127.0.0.1:5010/split_payment_details"

# These exchanges may need to be changed specific to this MS
exchangename = amqp_connection.secrets['exchangename'] #transfer_funds_topic
exchangetype = amqp_connection.secrets['exchangetype'] #topic 

#create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

@app.route("/split_payment", methods=['POST'])
def split_payment():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            details = request.get_json()
            print("\nReceived a payment split request in JSON:", details)

            # do the actual work
            # 1. Send split_payment details from UI { currUserBAN, currUserFullname, curUserPhoneNum, currUserEmail, requestedAmount, groupID }
            result = processSplitPayment(details)
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
                "message": "split_payment.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processSplitPayment(details):
    curr_user_ban = details["userBAN"]
    curr_user_fullname = details['userFullname']
    curr_user_hp = details["userPhoneNum"]
    curr_user_email = details['userEmail']

    #### these need to be named accordingly when submitted from frontend
    group_id = details['groupID']
    requested_amount = details['reqAmount']

    # 1. Send retrieved member_details to group_details microservice
    print('\n\n-----Invoking group_details microservice-----')

    split_payment_details = {  
                            "requester_phone_num": curr_user_hp,
                            "group_id": group_id,
                            "req_amount": requested_amount
                            }

    split_payment_details_result = invoke_http(group_details_URL, method="POST", json=split_payment_details)

    print('split_payment_details_result:', split_payment_details_result)

    message = json.dumps(split_payment_details_result)
    # Check the split payment details request result; if a failure, send it to the error microservice.
    code = split_payment_details_result["code"] 
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Publishing the (group_details error) message with routing_key=group_details.error-----')
        message = json.dumps(split_payment_details_result)
        channel.basic_publish(exchange=exchangename, routing_key="group_details.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nGroup_details MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), split_payment_details_result)


        # 7. Return error
        return {
            "code": 400,
            "data": {"split_payment_details_result": split_payment_details_result},
            "message": "Group_details split payment details sent for error handling."
        }
    
    else:
        # 4. Record group_details
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (group_details transfer details) message with routing_key=group_details.details-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        channel.basic_publish(exchange=exchangename, routing_key="group_details.details", 
            body=message)
        
    print("\nSplit payment details creation request published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 2. Send the relevant info {senderFullname, recipientFullname, senderEmail, recipientEmail} to notification microservice
    # Invoke the notification microservice
    print('\n\n-----Invoking notification microservice-----')

    print('\n\n-----Publishing the (notification details) message with routing_key=notification.details-----')
    requested_members_list = split_payment_details_result["data"]["requested_members_details"]
    for requested_member in requested_members_list:
        data = {
            "data": {
                "requested_user_fullname": requested_member["member_fullname"],
                "requested_user_email": requested_member["member_email"],
                "requester_fullname": curr_user_fullname,
                "group_name": requested_member["group_name"],
                "indiv_req_amount": split_payment_details_result["data"]["request_amount"],
                "reqDateTime": split_payment_details_result["data"]["datetime"]
                },
            "notification_type": "split_request"
            }
        message = json.dumps(data)
        channel.basic_publish(exchange=exchangename, routing_key="notification.details", body=message)

    # 3. Return successful split_request creation results
    return {
        "code": 201,
        "data": {
            "split_request_result": split_payment_details_result["data"]["created_split_request"],
            "requested_member_result": split_payment_details_result["data"]["created_requested_members"]
            }
        }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) +
          " for transferring funds...")
    app.run(host="0.0.0.0", port=5300, debug=True)