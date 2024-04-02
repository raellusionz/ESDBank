#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

from enum import Enum

import sys
from email_functions import sendCreateGroupNotif, sendSplitRequestNotif, sendTransferFundsNotif

import amqp_connection
import json
import pika

# n_queue_name = amqp_connection.secrets['n_queue_name'] # "Notification"

# exchangename = amqp_connection.secrets['exchangename'] #transfer_funds_topic
# exchangetype = amqp_connection.secrets['exchangetype'] #topic 

n_queue_name = "Notification" # "Notification"

exchangename = "transfer_funds_topic" #transfer_funds_topic
exchangetype = "topic" #topic

#create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status

def receiveEmailDetails(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=n_queue_name, on_message_callback=callback, auto_ack=True)
        print('notification microservice: Consuming from queue:', n_queue_name)
        channel.start_consuming() # an implicit loop waiting to receive messages; 
        #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"notification microservice: Failed to connect: {e}") 

    except KeyboardInterrupt:
        print("notification microservice: Program interrupted by user.")

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nnotification microservice: Received details from " + __file__)
    try:
        payload = json.loads(body)
        notification_type = payload["notification_type"]
        print(notification_type)
        if notification_type and notification_type == "create_group":
            processCreateGroupNotification(payload["data"])
        elif notification_type and notification_type == "split_request":
            processSplitRequestNotification(payload["data"])
        else:
            processTransferFundsNotification(payload)
    
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
    print()

def processSplitRequestNotification(details):
    print("Processing SplitRequest notification details:")
    print(details)

    requesterName = details["requester_fullname"]
    payerName = details["requested_user_fullname"]
    payerEmail = details["requested_user_email"]
    requestAmount = details["indiv_req_amount"]
    groupName = details["group_name"]
    requestDateTime = details["reqDateTime"]
    print()  # print a new line feed as a separator

    try:
        sendSplitRequestNotif(requesterName, payerName, payerEmail, requestAmount, groupName, requestDateTime)
        result = {
                "code": 201,
                "message": "Notification mails of split request successfully sent to requested users."
                }
        code = result["code"]
        message = json.dumps(result)

    except:
        result = {
                "code": 500,
                "message": "An error occurred sending the notification emails of split request."
                }
        code = result["code"]
        message = json.dumps(result)

        print('\n\n-----Publishing the (notification error) message with routing_key=notification.error-----')
        channel.basic_publish(exchange=exchangename, routing_key="notification.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))
        print("\nNotification MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), result)
        
    else:
        print('\n\n-----Publishing the (notification activity) message with routing_key=notification.activity-----')
        channel.basic_publish(exchange=exchangename, routing_key="notification.activity", 
                body=message)
        print("\nNotification activity published to the RabbitMQ Exchange.")

def processCreateGroupNotification(details):
    print("Processing CreateGroup notification details:")
    print(details)

    inviter = details["inviter"]
    invitee = details["invitee"]
    email = details["email"]
    group_name = details["group_name"]
    print()  # print a new line feed as a separator

    try:
        sendCreateGroupNotif(inviter, invitee, email, group_name)
        result = {
                "code": 201,
                "message": "Notification mails of group invite successfully sent."
                }
        code = result["code"]
        message = json.dumps(result)

    except:
        result = {
                "code": 500,
                "message": "An error occurred sending the notification emails of group invite."
                }
        code = result["code"]
        message = json.dumps(result)

        print('\n\n-----Publishing the (notification error) message with routing_key=notification.error-----')
        channel.basic_publish(exchange=exchangename, routing_key="notification.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))
        print("\nNotification MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), result)
        
    else:
        print('\n\n-----Publishing the (notification activity) message with routing_key=notification.activity-----')
        channel.basic_publish(exchange=exchangename, routing_key="notification.activity", 
                body=message)
        print("\nNotification activity published to the RabbitMQ Exchange.")

def processTransferFundsNotification(details):
    print("Processing transferFunds notification details:")
    print(details)

    senderFullname = str(details["data"]["senderFullname"])
    senderEmail = str(details["data"]["senderEmail"])
    recipientFullname = str(details["data"]["recipientFullname"])
    recipientEmail = str(details["data"]["recipientEmail"])
    amount = str(details["data"]["amount"])
    transactionDate = str(details["data"]["transactionDate"])
    transactionID = str(details["data"]["transactionID"])
    senderContent = "Sent to"
    recipientContent = "Received from"
    print()  # print a new line feed as a separator

    try:
        sendTransferFundsNotif(senderFullname, recipientFullname, senderEmail, amount, transactionDate, transactionID, senderContent)
        sendTransferFundsNotif(recipientFullname, senderFullname, recipientEmail, amount, transactionDate, transactionID, recipientContent)
        result = {
                "code": 201,
                "message": "Notification mails of fund transferral successfully sent."
                }
        code = result["code"]
        message = json.dumps(result)

    except:
        result = {
                "code": 500,
                "message": "An error occurred sending the notification emails of fund transferral."
                }
        code = result["code"]
        message = json.dumps(result)

        print('\n\n-----Publishing the (notification error) message with routing_key=notification.error-----')
        channel.basic_publish(exchange=exchangename, routing_key="notification.error", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))
        print("\nNotification MS status ({:d}) published to the RabbitMQ Exchange:".format(
            code), result)
        
    else:
        print('\n\n-----Publishing the (notification activity) message with routing_key=notification.activity-----')
        channel.basic_publish(exchange=exchangename, routing_key="notification.activity", 
                body=message)
        print("\nNotification activity published to the RabbitMQ Exchange.")


if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("notification microservice: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("notification microservice: Connection established successfully")
    channel = connection.channel()
    receiveEmailDetails(channel)
