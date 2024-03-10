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
    from flask import Flask, request, jsonify
    from flask_sqlalchemy import SQLAlchemy, extract
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

    app = Flask(__name__)

    # PostgreSQL URI format: postgresql://username:password@host:port/database_name 

    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}" 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    
    db = SQLAlchemy(app)

    class txn_hist_db (db.Model): #Book
        __tablename__ = DB_NAME #book

        txn_id = db.Column(primary_key=True, nullable=False)
        crban  = db.Column(db.String(20))
        drban  = db.Column(db.String(20))
        txn_amt  = db.Column(db.Float(precision=2), nullable=False)
        txn_time = db.Column(db.String(100))


        def __init__(self, txn_id, crban, drban, txn_amt, txn_time):
            self.txn_id = txn_id
            self.crban = crban
            self.drban = drban
            self.txn_amt = txn_amt
            self.txn_time = txn_time


        def json(self):
            return {"txn_id": self.txn_id, "txn_id": self.crban, "price": self.drban, "txn_amt": self.txn_amt,"txn_time": self.txn_time}

    @app.route("/" + DB_NAME) #book
    def get_transaction_by_month(txn_time): #isbn13

        transaction_month = txn_time.split('-')[1]
        transactionlog_month = db.session.scalars(
            db.select(txn_hist_db).filter(extract('month', txn_hist_db.datetime_column) == transaction_month).limit(1)
        ).first()

        if len(transactionlog_month):
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "Transaction for" + transaction_month : [transaction.json() for transaction in transactionlog_month]
                    }
                }
            )
        return jsonify(
            {
                "code": 404,
                "message": "There are no transactions."
            }
        ), 404


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
    
