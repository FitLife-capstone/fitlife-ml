import os
import psycopg2

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_HOST'),
            dbname=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            sslmode='disable'
        )
        print(f"Connected to {os.environ.get('POSTGRES_DB')} database")
        return conn
    except Exception as e:
        print(f"Error: Could not make connection to the PostgreSQL database")
        print(e)
        return None