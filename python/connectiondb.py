def specific_phone_number_connection(number):
    import psycopg2
    
    DB_NAME = "verceldb"
    DB_USER = "default"
    DB_PASS = "vHFyts8wa4PK"
    DB_HOST = "ep-shiny-wave-a4w35od7-pooler.us-east-1.aws.neon.tech"
    DB_PORT = "5432"
    
    conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    print("Database connected successfully")

    # Creating a cursor
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_acct_details_db where user_hp =" + number )
    rows = cur.fetchall()
    for data in rows:
        print(data)

    print('Data fetched successfully')
    conn.close()


def transaction_log_month(acct_number,month):
    import psycopg2

    DB_NAME = "verceldb"
    DB_USER = "default"
    DB_PASS = "vHFyts8wa4PK"
    DB_HOST = "ep-shiny-wave-a4w35od7-pooler.us-east-1.aws.neon.tech"
    DB_PORT = "5432"
    
    conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    print("Database connected successfully")

    ## Start to retrieve data

    # Creating a cursor
    cur = conn.cursor()
    cur.execute("SELECT * FROM txn_hist_db where (crban = '" + acct_number + "' or drban = '" + acct_number + "') and EXTRACT(MONTH FROM CAST(txn_time AS DATE)) =" + str(month))

    rows = cur.fetchall()
    transactionloggermonth = []
    for data in rows:
        transactionloggermonth.append(data)

    ## End to retrieve data
    
    conn.close()
    return transactionloggermonth

    #print('Data fetched successfully')


def transaction_log(acct_number):
    import psycopg2
    
    DB_NAME = "verceldb"
    DB_USER = "default"
    DB_PASS = "vHFyts8wa4PK"
    DB_HOST = "ep-shiny-wave-a4w35od7-pooler.us-east-1.aws.neon.tech"
    DB_PORT = "5432"
    
    conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    print("Database connected successfully")

    # Creating a cursor
    cur = conn.cursor()
    cur.execute("SELECT * FROM txn_hist_db where (crban = '" + acct_number + "' or drban = '" + acct_number + "')")
    rows = cur.fetchall()
    transactionlogger = []
    for data in rows:
        transactionlogger.append(data)

    conn.close()
    return transactionlogger

    #print('Data fetched successfully')
    
