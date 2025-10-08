import pandas as pd
from dbConfiguration import get_connection

    finally:

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

def get_players(a: int , b: int ):
    conn = get_connection()
    try:
        query = "SELECT DISTINCT name FROM players p INNER JOIN match_events e ON p.player_id = e.player_id WHERE match_id = %s and e.team_id = %s and e.period_display_name = 'FirstHalf' ORDER BY name"
        df = pd.read_sql(query, conn, params=(int(a), int(b)))
        return df
    finally:
        conn.close()


def get_match_events(a: int):
    conn = get_connection()
    try:
        query = "SELECT event_id, minute, second, team_id, player_id, x, y, end_x, end_y, is_touch, blocked_x, blocked_y, goal_mouth_z, goal_mouth_y,is_shot, card_type, is_goal, type_display_name, outcome_display_name, period_display_name, match_id FROM match_events WHERE match_id = %s ORDER BY match_id DESC minute, second"
        df = pd.read_sql(query, conn, params=(int(a)))
        return df
    finally:
        conn.close()