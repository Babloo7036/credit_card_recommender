import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        dbname="credit_cards",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            issuer VARCHAR(50),
            annual_fee INTEGER,
            reward_type VARCHAR(50),
            reward_rate FLOAT,
            eligibility_income INTEGER,
            perks TEXT,
            apply_link VARCHAR(200)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def fetch_cards():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM cards")
    cards = cur.fetchall()
    cur.close()
    conn.close()
    return cards

def insert_dummy_data():
    conn = get_db_connection()
    cur = conn.cursor()
    dummy_cards = [
        ('HDFC Regalia', 'HDFC Bank', 2500, 'Travel Points', 4.0, 50000, '4 lounge visits/year, 2% cashback on dining', 'https://apply.hdfcbank.com/regalia'),
        ('SBI Elite', 'SBI', 4999, 'Reward Points', 3.5, 60000, '6 lounge visits/year, 5% cashback on groceries', 'https://apply.sbi.com/elite'),
        ('Axis Magnus', 'Axis Bank', 10000, 'Travel Points', 5.0, 75000, '8 lounge visits/year, 3% cashback on travel', 'https://apply.axisbank.com/magnus'),
        ('ICICI Sapphire', 'ICICI Bank', 3500, 'Cashback', 2.5, 55000, '2 lounge visits/year, Amazon vouchers', 'https://apply.icicibank.com/sapphire'),
        ('Amex Platinum', 'American Express', 60000, 'Reward Points', 6.0, 100000, 'Unlimited lounge access, 5% cashback on dining', 'https://apply.amex.com/platinum')
    ]
    cur.executemany(
        "INSERT INTO cards (name, issuer, annual_fee, reward_type, reward_rate, eligibility_income, perks, apply_link) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        dummy_cards
    )
    conn.commit()
    cur.close()
    conn.close()