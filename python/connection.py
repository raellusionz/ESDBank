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


def transaction_call_cr():
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
