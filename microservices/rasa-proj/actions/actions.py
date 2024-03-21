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
from invokes import invoke_http
from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher



class ActionProvideFinancialAdvice(Action):

    def name(self):
        return "action_provide_financial_advice"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):
        bankId = 123456789012
        transaction_hist_db = invoke_http()

        user_goals = {
        "goals": {
            "saving_goal_percentage": 20,
            "total_expenditure_goal_percentage": 80,
            "expenditure_goals": {
            "Funds Transfer": 5,
            "Necessities": 30,
            "Transportation": 10,
            "Food & Drink": 15,
            "Shopping & Entertainment": 15,
            "Others": 5
            }
        }
        }

        # Calculate total income for determining percentage goals
        total_income = sum(item["txn_amt"] for item in transaction_hist if item["category"] == "Income")

        # Initialize a dictionary to hold actual spending percentages
        actual_spending_percentages = {category: 0 for category in user_goals["goals"]["expenditure_goals"]}
        total_spent = 0

        # Calculate actual spending percentages
        for transaction in transaction_hist:
            category = transaction["category"]
            amount = transaction["txn_amt"]
            if category in actual_spending_percentages and (transaction["drban"] == bankId):  # Checking if bank was the one transferring
                actual_spending_percentages[category] += amount  # Convert to positive number for summing
                total_spent += amount  # Convert to positive and sum

        # Convert amounts to percentages of income
        for category, amount in actual_spending_percentages.items():
            actual_spending_percentages[category] = (amount / total_income) * 100

        # Generate advice for each category
        advice = []
        for category, goal_percentage in user_goals["goals"]["expenditure_goals"].items():
            actual_percentage = actual_spending_percentages.get(category, 0)
            if actual_percentage > goal_percentage:
                advice.append(f"Your spending on {category} is {actual_percentage:.2f}% of your income, which is above your goal of {goal_percentage}%. Consider cutting back in this area.")

        # Check total expenditure goal
        total_spent_percentage = (total_spent / total_income) * 100
        if total_spent_percentage > user_goals["goals"]["total_expenditure_goal_percentage"]:
            advice.append(f"Your total spending is {total_spent_percentage:.2f}% of your income, exceeding your goal of {user_goals['goals']['total_expenditure_goal_percentage']}%. Review your expenditures to find areas to save.")

        if not advice:
            advice.append("You are within your spending goals for all categories. Great job managing your finances!")

        advice_message = " ".join(advice)  # Assuming advice is a list of strings
        dispatcher.utter_message(text=advice_message)

        # Since there's no specific event to return, return an empty list
        return []