import pandas as pd
from dbConfiguration import get_connection

def get_players():
    conn = get_connection()
    try:
        query = "SELECT player_id, shirt_no, name, position, age, team_id FROM players ORDER BY name"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

