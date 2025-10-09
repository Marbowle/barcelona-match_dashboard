import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import queries
from mplsoccer import Pitch

st.title("Match Dashboard")
st.header("Match Statistics")
st.caption("Here you will see the match statistics between Barcelona and a team of your choice. The statistics are from the last 2024/2025 season.")

teams_df = queries.get_teams()

col1, col2 = st.columns(2)
with col1:
    base_team = "Barcelona"
    st.write(base_team)
with col2:
    other_team = [t for t in teams_df['name'] if t!=base_team]
    compare_team = st.selectbox('Select a comparison team', other_team)

barcelona_filename = base_team.lower() + "_logo.png"
barcelona_logo_path = f"team_logos/{barcelona_filename}"

compare_team_filename = compare_team.lower() + "_logo.png"
compare_team_logo_path = f"team_logos/{compare_team_filename}"

col1, col2 = st.columns(2)
with col1:
    st.image(barcelona_logo_path, width = 200)
with col2:
    if os.path.exists(compare_team_logo_path):
        st.image(compare_team_logo_path, width = 100)
    else:
        st.image("team_logos/football.png", width = 100)

barcelona_id = int(teams_df.loc[teams_df['name'] == base_team, "team_id"].iloc[0])
compare_team_id = int(teams_df.loc[teams_df['name'] == compare_team, "team_id"].iloc[0])

#tutaj zabezpieczenie do tego, jeżeli nie mamy wybranego żadnego id meczu
df = queries.get_match_id(barcelona_id, compare_team_id)
match_id = st.selectbox('Select a match', df['match_id'].astype(int).tolist(), index=None, placeholder="Choose a match")
if match_id is None:
    st.info("Choose your match ID to see the list of players")
    st.stop()

barcelona_players = queries.get_players(int(match_id), int(barcelona_id))
compare_team_players = queries.get_players(int(match_id), int(compare_team_id))

#zabezpieczneie przed pustym wyborem
if barcelona_players is None or barcelona_players.empty or compare_team_players is None or compare_team_players.empty:
    st.info("No players selected")
    st.stop()


barca_names = (barcelona_players['name'].astype(str).str.strip().replace({"": None}).dropna().unique())
barca_names = barca_names.tolist()

opp_names = (compare_team_players['name'].astype(str).str.strip().replace({"": None}).dropna().unique())
opp_names = opp_names.tolist()

col1, col2 = st.columns(2)
with col1:
    barcelona_player = st.selectbox("Select a Barcelona player", barca_names, index=None, placeholder="Choose a Barcelona player", key="barca_player_name")
with col2:
    compare_team_player = st.selectbox("Select an opposing player", opp_names, index=None, placeholder="Choose a opponent player", key="opp_player_name")

#zabezpieczenie przed wyborem zawodnika
if barcelona_player is None  or compare_team_player is None:
    st.info("Choose players from both teams")
    st.stop()

def get_player_id(players_df: pd.DataFrame, player_name: str):
    s = players_df.loc[players_df['name'].astype(str).str.strip() == str(player_name).strip(), 'player_id'].dropna()
    return int(s.iloc[0]) if len(s) > 0 else None

barcelona_player_id = get_player_id(barcelona_players, barcelona_player)
compare_team_player_id = get_player_id(compare_team_players, compare_team_player)

if barcelona_player_id is None or compare_team_player_id is None:
    st.warning("No players selected")
    st.stop()


#eventy dla danego teamu + dodanie eventów dla danego piłkarza z drużyny
match_df = queries.get_match_events(int(match_id))

#zwracanie przefiltrowanego df, ze wzgledu na piłkarza i mecz
def filter_data(df, team, player):
    if team:
        df = df[df['team_id'] == team]
    if player:
        df = df[df['player_id'] == player]
    return df

#przefiltrowane df ze wzgledu na piłkarza i team
barcelona_df = filter_data(match_df, barcelona_id, barcelona_player_id)
compare_team_df = filter_data(match_df, compare_team_id, compare_team_player_id)


#stowrzenie funkcji rysującej boisko
def get_pitch():
    return Pitch(pitch_type='wyscout')

#tworzenie shot_mapy, dla piłkarza
def create_shotmap(df, title: str):
    pitch = get_pitch()
    fig, ax = pitch.draw()

    if df is None or df.empty:
        ax.set_title(title, fontsize=10, pad= 10)
        ax.text(50, 50, "Brak danych", ha="center", va="center", alpha=0.6)
        return fig

    is_shot_bool = df.get('is_shot', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    is_goal_bool = df.get('is_goal', pd.Series(False, index=df.index)).fillna(False).astype(bool)

    type_str = df.get('type_display_name', pd.Series("", index=df.index)).fillna("").astype(str).str.lower()

    shot_mask = is_shot_bool & type_str.str.contains("shot", na=False) | type_str.eq('goal')

    goal_mask = is_goal_bool | type_str.eq('goal')

    shots = df.loc[shot_mask].dropna(subset=['x', 'y'])

    if shots.empty:
        return None

    goals = df.loc[shot_mask & goal_mask]
    others = df.loc[shot_mask & ~goal_mask]

    ax.scatter(others['x'], others['y'], s=60, c='red')
    ax.scatter(goals['x'], goals['y'], s=90, c='green')

    ax.set_title(title, fontsize=20, pad = 10)
    return fig

col1, col2 = st.columns(2)
with col1:
    fig_home = create_shotmap(barcelona_df, "Barcelona shots by player")
    if fig_home is None:
        st.write("This player has no shots")
    else:
        st.pyplot(fig_home,use_container_width=True)
with col2:
    fig_compare_team = create_shotmap(compare_team_df, "Compared team shots by player")
    if fig_compare_team is None:
        st.write("This player has no shots")
    else:
        st.pyplot(fig_compare_team,use_container_width=True)




