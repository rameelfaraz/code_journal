import psycopg
from config import DB_PASSWORD

def get_connection():
    return psycopg.connect(
        host="localhost",
        dbname="employee_analytics",
        user="postgres",
        password=DB_PASSWORD
    )

if __name__ == "__main__":
    conn = get_connection()
    print("Connected successfully!")
    conn.close()