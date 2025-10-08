import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import queries

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
    st.info("Choose your match id to see a statistic")
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

barcelona_team = match_df[match_df['team_id'] == barcelona_id]
compare_team = match_df[match_df['team_id'] == compare_team_id]

#zwracanie przefiltrowanego df, ze wzgledu na piłkarza i mecz

#funkcja do wyświetlania podań danego piłkarza
#def creat_pass_map_players(match_df,team_id, player_id):
 #   match_df = match_df[match_df['type_display_name'] == 'Pass']


#funkcja do wyświetlania shot map
#def create_shot(match_df,team_id):
 #   match_df = match_df[match_df['type_display_name'] == 'Goal'].reset_index(drop=True)
  #  match_df = match_df[match_df['team_id'] == team_id]


