from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys

from invokes import invoke_http

import pika
import json
import amqp_connection

app = Flask(__name__)
CORS(app)

# routes to group_details function that updates the request status
group_details_URL = "http://127.0.0.1:5010/requestedMembers/updateRequest/"
transfer_funds_URL = "http://127.0.0.1:5100/transfer_funds"

# These exchanges may need to be changed specific to this MS
# exchangename = amqp_connection.secrets['exchangename'] #transfer_funds_topic
# exchangetype = amqp_connection.secrets['exchangetype'] #topic 
exchangename = "transfer_funds_topic" #transfer_funds_topic
exchangetype = "topic"  #topic 

#create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

# 
@app.route("/handle_split_reply", methods=['POST'])
def handle_split_reply():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            details = request.get_json()
            print("\nReceived a split request reply in JSON:", details)

            # do the actual work
            # 1. Send these details from UI to processSplitReply {payingUserFullname, payingUserEmail, payingUserBAN, requesterUserPhoneNum, ReqID, indivReqAmount, replyStatus("accept" or "decline) }
            result = processSplitReply(details)
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
                "message": "handle_split_reply.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processSplitReply(details):
    payingUserFullname = details["payingUserFullname"]
    payingUserEmail = details["payingUserEmail"]
    payingUserBan = details["payingUserBan"]
    requesterUserPhoneNum = details['requesterUserPhoneNum']
    request_id = details["request_id"]
    amount_to_pay = details['amount_to_pay']
    reply = details['reply']

    # 1. Send split__reply details to group_details microservice to update status log
    print('\n\n-----Invoking group_details microservice-----')
    
    # Route is: /requestedMembers/updateRequest/<string:user_ban>/<int:req_id>/<string:reply>
    split_reply_details_result = invoke_http(group_details_URL+f"{payingUserBan}/{request_id}/{reply}", method="PUT")

    print('split_payment_details_result:', split_reply_details_result)

    message = json.dumps(split_reply_details_result)
    # Check the split reply details result; if a failure, send it to the error microservice.
    code = split_reply_details_result["code"] 
    if code not in range(200, 300):

        # Inform the error microservice
        print('\n\n-----Publishing the (group_details error) message with routing_key=group_details.error-----')
        message = json.dumps(split_reply_details_result)
        channel.basic_publish(exchange=exchangename, routing_key="group_details.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))

        print("\nGroup_details MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), split_reply_details_result)


        # Return error
        return {
            "code": 400,
            "data": {"split_reply_details_result": split_reply_details_result},
            "message": "Group_details split reply details sent for error handling."
        }
    
    else:
        # 2. Record group_details
        # record the activity log anyway
        #print('\n\n-----Invoking activity_log microservice-----')
        print('\n\n-----Publishing the (group_details transfer details) message with routing_key=group_details.details-----')        

        # invoke_http(activity_log_URL, method="POST", json=order_result)            
        channel.basic_publish(exchange=exchangename, routing_key="group_details.details", 
            body=message)
        
    print("\nSplit reply details published to RabbitMQ Exchange.\n")
    # - reply from the invocation is not used;
    # continue even if this invocation fails


    # 3. Check if reply is accept or decline, if accept then call transfer_funds else nth happens
    if reply == "accept":

        # Send the relevant info {senderFullname, recipientFullname, senderEmail, recipientEmail} to transfer_funds complex microservice
        data = {
            "senderFullname": payingUserFullname,
            "senderBAN": payingUserBan,
            "senderEmail": payingUserEmail,
            "recipientPhoneNumber": requesterUserPhoneNum,
            "transactionAmount": amount_to_pay,
            "category": "Fund Transfer"
        }

        # Invoke the transfer_funds microservice

        print('\n\n-----Invoking transfer funds microservice-----')
        transfer_funds_result = invoke_http(transfer_funds_URL, method='POST', json=data )
        print('transfer_funds_result:', transfer_funds_result)


        code = transfer_funds_result["code"]
        message = json.dumps(transfer_funds_result)


        if code not in range(200, 300):

            print('\n\n-----Publishing the (transfer funds error) message with routing_key=transfer_funds.error-----')
            channel.basic_publish(exchange=exchangename, routing_key="transfer_funds.error", 
                body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
            # make message persistent within the matching queues until it is received by some receiver 
            # (the matching queues have to exist and be durable and bound to the exchange)


            # - reply from the invocation is not used; 
            # continue even if this invocation fails
            print("\nTransfer_funds MS status ({:d}) published to the RabbitMQ Exchange:".format(
                code), transfer_funds_result)


            # 5. Return error
            return {
                "code": 500,
                "data": {"transfer_funds_result": transfer_funds_result},
                "message": "Transfer funds result failure sent for error handling."
            }
        
        else:
            # 4. Record new transfer_funds activity
            print('\n\n-----Publishing the (transfer_funds details) message with routing_key=transfer_funds.details-----')        
            channel.basic_publish(exchange=exchangename, routing_key="transfer_funds.details", 
                body=message)

    # 3. Return successful split_reply results
    return {
        "code": 201,
        "data": {
            "split_reply_result": split_reply_details_result,
            }
        }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask for " + os.path.basename(__file__) +
          " for handling split request responses funds...")
    app.run(host="0.0.0.0", port=5400, debug=True)