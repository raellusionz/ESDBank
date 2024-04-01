import calendar
def transactionjsondata(transactions):
    transactions_dict_full = []
    for transaction in transactions:
        # Assuming transaction is a tuple with specific fields, convert it to a dictionary
        transaction_dict = {
            "txn_id": transaction[0],  # Replace field1, field2, etc. with your actual field names
            "crban": transaction[1],
            "drban": transaction[2],
            "txn_amt": transaction[3],
            "txn_time": transaction[4],
        }
        transactions_dict_full.append(transaction_dict)
    return transactions_dict_full

def get_month_name(month_number):
    return calendar.month_name[month_number]


def monthlyspendcalc(accountnumber,transactions_dict_month):
    monthspendpos = 0
    monthspendneg = 0
    for txn in transactions_dict_month:
        if txn["crban"] == accountnumber:
            monthspendpos += txn["txn_amt"]
        if txn["drban"] == accountnumber:
            monthspendneg += txn["txn_amt"]
    return [monthspendpos,monthspendneg]