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


def get_teams():
    conn = get_connection()
    try:
        query = "SELECT team_id, name, manager_name, country_name  FROM teams ORDER BY name"

        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

def get_match_id(a: int, b: int):
    conn = get_connection()
    try:
        query = "SELECT match_id FROM match_events WHERE team_id IN (%s,%s) GROUP BY match_id HAVING COUNT(DISTINCT team_id) = 2 ORDER BY match_id DESC"
        df = pd.read_sql(query, conn, params=(int(a), int(b)))
        return df
    finally:
        conn.close()