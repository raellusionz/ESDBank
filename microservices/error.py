#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import amqp_connection
import json
import pika

# e_queue_name = amqp_connection.secrets['e_queue_name'] #Error
e_queue_name = "Error"

def receiveError(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=e_queue_name, on_message_callback=callback, auto_ack=True)
        print('error microservice: Consuming from queue:', e_queue_name)
        channel.start_consuming() # an implicit loop waiting to receive messages; 
        #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"error microservice: Failed to connect: {e}") 

    except KeyboardInterrupt:
        print("error microservice: Program interrupted by user.")

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nerror microservice: Received an error by " + __file__)
    processError(body)
    print()

def processError(errorMsg):
    print("error microservice: Printing the error message:")
    try:
        error = json.loads(errorMsg)
        print("--JSON:", error)
    except Exception as e:
        print("--NOT JSON:", e)
        print("--DATA:", errorMsg)
    print()

if __name__ == "__main__": # execute this program only if it is run as a script (not by 'import')    
    print("error microservice: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("error microservice: Connection established successfully")
    channel = connection.channel()
    receiveError(channel)