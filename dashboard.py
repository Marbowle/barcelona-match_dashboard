import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import queries
from mplsoccer import Pitch, VerticalPitch

st.title("Match Dashboard")
st.header("Match Statistics")
st.caption("Here you will see match statistic between 2 teams Barcelona and your choice. The statistics are from last season 2024/2025")

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
    st.info("Choose your match id to see a list of players")
    st.stop()

barcelona_players = queries.get_players(int(match_id), int(barcelona_id))
compare_team_players = queries.get_players(int(match_id), int(compare_team_id))

col1, col2 = st.columns(2)
with col1:
    barcelona_player = st.selectbox("Select a player", barcelona_players, index=None)
with col2:
    compare_team_player = st.selectbox("Select a player", compare_team_players, index=None)

#eventy dla danego teamu + dodanie eventów dla danego piłkarza z drużyny
match_df = queries.get_match_events(match_id)

#otrzymywanie id piłkarza po wywołaniu
def get_player_id(players_df, player):
    s = players_df.loc[players_df['name'] == player, "player_id"]
    return s

barcelona_player_id = int(get_player_id(barcelona_players, barcelona_player))
compare_team_player_id = int(get_player_id(compare_team_players, compare_team_player))

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
    return VerticalPitch(pitch_type='statsbomb', half=True)

#tworzenie shot_mapy, dla piłkarza
def create_shotmap(df, title: str):
    pitch = get_pitch()
    fig, ax = pitch.draw()

    df_shots = df.copy()
    shots = df_shots[df_shots['is_shot'] == 'true']
    goals = shots[shots['is_goal'] == 'true']
    others = goals[goals['is_goal'] == 'false']

    ax.scatter(others['x'], others['y'], s=60, c='red')
    ax.scatter(goals['x'], goals['y'], s=90, c='green')

    ax.set_title(title, fontsize=10, pad = 10)
    return fig

col1, col2 = st.columns(2)
with col1:
    fig_home = create_shotmap(barcelona_df, "Barcelona shots by player")
    st.pyplot(fig_home,use_container_width=True)
with col2:
    fig_compare_team = create_shotmap(compare_team_df, "Compared team shots by player")
    st.pyplot(fig_compare_team,use_container_width=True)


