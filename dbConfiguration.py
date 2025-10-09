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

def _get(name, default=None):
    return st.secrets.get(name) or os.getenv(name)


def get_connection():
    cfg = {
        'host':  _get("SUPABASE_HOST"),
        'database': _get("SUPABASE_DB"),
        'user': _get("SUPABASE_USER"),
        'password': _get("DB_PASSWORD"),
        'port': _get("SUPABASE_PORT")
    }
    return psycopg2.connect(**cfg)

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
