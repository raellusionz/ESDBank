#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import amqp_connection
import json
import pika


# al_queue_name = amqp_connection.secrets['al_queue_name'] #Activity_Log
al_queue_name = "Activity_Log"
def receiveActivityLog(channel):
    try:
        # set up a consumer and start to wait for coming messages
        channel.basic_consume(queue=al_queue_name, on_message_callback=callback, auto_ack=True)
        print('activity_log: Consuming from queue:', al_queue_name)
        channel.start_consuming()  # an implicit loop waiting to receive messages;
             #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.
    
    except pika.exceptions.AMQPError as e:
        print(f"activity_log: Failed to connect: {e}") # might encounter error if the exchange or the queue is not created

    except KeyboardInterrupt:
        print("activity_log: Program interrupted by user.")

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nactivity_log: Received details from " + __file__)
    processActivityLog(json.loads(body))
    print()

def processActivityLog(activity):
    print("activity_log: Recording the most recent activity:")
    print(activity)

if __name__ == "__main__":  # execute this program only if it is run as a script (not by 'import')
    print("activity_log: Getting Connection")
    connection = amqp_connection.create_connection() #get the connection to the broker
    print("activity_log: Connection established successfully")
    channel = connection.channel()
    receiveActivityLog(channel)
