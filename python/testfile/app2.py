import sys
sys.path.append('../')  # Add the parent directory of testfile to the Python path

from connectiondb import * 

accountnumber = "334455667788"
month = 2
data = transaction_log_month(accountnumber,month)
monthspendpos = 0
monthspendneg = 0
for txn in data:
    if txn[2] == accountnumber:
        monthspendpos += txn[3]
    if txn[1] == accountnumber:
        monthspendneg += txn[3]

print(f"Money Added to Bank : {monthspendpos}")
print(f"Money Deducted from Bank : {monthspendneg}")