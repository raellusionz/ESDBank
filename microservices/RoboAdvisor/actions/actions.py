# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parents[2]))
from invokes import invoke_http
import amqp_connection


exchangename = amqp_connection.secrets['exchangename'] #transfer_funds_topic
exchangetype = amqp_connection.secrets['exchangetype'] #topic 

#create a connection and a channel to the broker to publish messages to activity_log, error queues
connection = amqp_connection.create_connection() 
channel = connection.channel()

#if the exchange is not yet created, exit the program
if not amqp_connection.check_exchange(channel, exchangename, exchangetype):
    print("\nCreate the 'Exchange' before running this microservice. \nExiting the program.")
    sys.exit(0)  # Exit with a success status


# class ActionExtractBankID(Action):
#     def name(self):
#         return "action_extract_bank_id"

#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict):
#         metadata = tracker.latest_message.get('metadata', {})
#         bankID = metadata.get('bankID')
#         if bankID is not None:
#             return [SlotSet("bankID", bankID)]
#         return []

class ActionProvideFinancialAdvice(Action):

    def name(self):
        return "action_provide_financial_advice"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        metadata = tracker.latest_message.get('metadata', {})
        bankId = metadata.get('bankID')

        transaction_hist = invoke_http("http://127.0.0.1:5002/transactionHistory/bank_acct_id/" + str(bankId), method='GET')
        transaction_hist = transaction_hist['data']
        user_saving_goals = invoke_http("http://127.0.0.1:5000/userPreference/user_saving_goal/" + str(bankId), method='GET')
        user_saving_goals = user_saving_goals['data']
        user_expenditure = invoke_http("http://127.0.0.1:5000/userPreference/user_expenditure/" + str(bankId), method='GET')
        user_expenditure = user_expenditure['data']

        # Calculate total income for determining percentage goals
        total_income = sum(int(item["txn_amt"]) for item in transaction_hist if item["category"] == "Income")

        # Initialize a dictionary to hold actual spending percentages
        actual_spending_percentages = {category: 0 for category in user_expenditure["breakdown"]}
        total_spent = 0

        # Calculate actual spending percentages
        for transaction in transaction_hist:
            category = transaction["category"]
            amount = transaction["txn_amt"]
            if category in actual_spending_percentages and (transaction["drban"] == str(bankId)):  # Checking if bank was the one transferring
                actual_spending_percentages[category] += int(amount)  # Convert to positive number for summing
                total_spent += amount  # Convert to positive and sum

        # Convert amounts to percentages of income
        for category, amount in actual_spending_percentages.items():
            actual_spending_percentages[category] = (amount / total_income) * 100

        # Generate advice for each category in HTML format
        advice = []
        for category, goal_percentage in user_expenditure["breakdown"].items():
            actual_percentage = actual_spending_percentages.get(category, 0)
            if actual_percentage > float(goal_percentage):
                advice.append(f"<li>Your spending on <strong>{category}</strong> is <strong>{actual_percentage:.2f}%</strong> of your income, which is above your goal of <strong>{goal_percentage}%</strong>. Consider cutting back in this area.</li>")

        # Check total expenditure goal
        total_spent_percentage = (total_spent / total_income) * 100
        if total_spent_percentage > float(user_expenditure["expanditure_target_percent"]):
            advice.append(f"<li>Your total spending is <strong>{total_spent_percentage:.2f}%</strong> of your income, exceeding your goal of <strong>{user_expenditure['expanditure_target_percent']}%</strong>. Review your expenditures to find areas to save.</li>")

        if not advice:
            advice.append("<li>You are within your spending goals for all categories. Great job managing your finances!</li>")
        else:
            advice_message = "<ul>" + " ".join(advice) + "</ul>"  # Concatenate advice items into an unordered list
            advice_message = "</br><h2>Based on your recent spending</h2>" + advice_message



        dispatcher.utter_message(text=advice_message)
        
        # publish message to activity_log
        payload = {"message": "successful run"}
        message = json.dumps(payload)
        channel.basic_publish(exchange=exchangename, routing_key="actions.details", 
            body=message)

        # Since there's no specific event to return, return an empty list
        return []
    

class ActionGenerateBankStatement(Action):

    def name(self):
        return "action_generate_bank_statement"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        metadata = tracker.latest_message.get('metadata', {})
        bankId = metadata.get('bankID')

        transaction_hist = invoke_http("http://127.0.0.1:5002/transactionHistory/bank_acct_id/" + str(bankId), method='GET')
        transaction_hist = transaction_hist['data']
        user_expenditure = invoke_http("http://127.0.0.1:5000/userPreference/user_expenditure/" + str(bankId), method='GET')
        user_expenditure = user_expenditure['data']

        # Filter transactions related to the user's bank ID
        user_transactions = [txn for txn in transaction_hist if txn["drban"] == str(bankId)]

        # Summarize transactions
        summary = {}
        for txn in user_transactions:
            category = txn["category"]
            amount = txn["txn_amt"]
            summary[category] = summary.get(category, 0) + amount

        # Generate statement message
        statements = []
        for category, total in summary.items():
            statements.append(f"<li><strong>{category}</strong>: ${round(total, 2)}</li>")

        statement_message = "<h2>Here's your bank statement:</h2><ul>" + "".join(statements) + "</ul>"

        # Send the message back to the user
        dispatcher.utter_message(text=statement_message)

        # publish message to activity_log
        payload = {"message": "successful run"}
        message = json.dumps(payload)
        channel.basic_publish(exchange=exchangename, routing_key="actions.details", 
            body=message)

        return []