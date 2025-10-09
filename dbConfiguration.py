import supabase
from dotenv import load_dotenv
import os
import psycopg2
from supabase import create_client
import streamlit as st
import os

dotenv_path = os.path.join(os.path.dirname(__file__), 'secrets.env')
if not os.path.exists(dotenv_path):
    print("No .env file found")
else:
    print("Found .env file")
    load_dotenv(dotenv_path)

load_dotenv(dotenv_path)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("SUPABASE_HOST"),
        database=os.getenv("SUPABASE_DB"),
        user=os.getenv("SUPABASE_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("SUPABASE_PORT")
    )

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

if __name__ == "__main__":
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        print("Połączono z baza danych poprawnie.")
        conn.close()
    except Exception as e:
        print("Błąd połączenia:", e)
