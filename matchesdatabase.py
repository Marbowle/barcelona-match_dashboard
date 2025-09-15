import json
import time

import numpy as np
import pandas as pd

from bs4 import BeautifulSoup

from pydantic import BaseModel
from typing import List, Optional

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from supabase import create_client
from dbConfiguration import get_supabase_client

import secrets

class MatchEvent(BaseModel):
    id: int
    event_id: int
    minute: int
    second: Optional[float] = None
    team_id: int
    player_id: int
    x: float
    y: float
    end_x: Optional[float] = None
    end_y: Optional[float] = None
    is_touch: bool
    blocked_x: Optional[float] = None
    blocked_y: Optional[float] = None
    goal_mouth_z: Optional[float] = None
    goal_mouth_y: Optional[float] = None
    is_shot: bool
    card_type: bool
    is_goal: bool
    type_display_name: str
    outcome_display_name: str
    period_display_name: str
    match_id: int
    qualifiers: List[Dict[str, Any]]

def insert_match_events(df, supabase):
    df = df.drop_duplicates(subset=['event_id'])
    events = []
    for x in df.to_dict(orient='records'):
        try:
            x['match_id'] = int(x['match_id'])
            event = MatchEvent(**x).model_dump()
            events.append(event)
        except Exception as e:
            print(f"Błąd w evencie: {e}")
    execution = supabase.table('match_events').upsert(events).execute()

class Player(BaseModel):
    player_id: int
    shirt_no: int
    name: str
    age: int
    position: str
    team_id: int

def insert_players(team_info, supabase):
    players = []
    for team in team_info:
        for player in team['players']:
            players.append({
                'player_id': player['playerId'],
                'team_id': team['team_id'],
                'shirt_no': player['shirtNo'],
                'name': player['name'],
                'position': player['position'],
                'age': player['age']
            })


    execution = supabase.table('players').upsert(players).execute()


class Team(BaseModel):
    team_id: int
    name: str
    manager_name: str
    country_name: str

def insert_teams(team_info, supabase):
    cleaned = []
    for team in team_info:
        team_clean= dict(team)
        team_clean.pop("players", None)
        cleaned.append(team_clean)

    supabase.table('teams').upsert(cleaned).execute()

#Supabase client
supabase = get_supabase_client()

driver = webdriver.Chrome()

import re

def extract_match_id_from_url(url):
    match = re.search(r'/matches/(\d+)', url)
    return int(match.group(1)) if match else None

def scrape_match_events(whoscored_url, driver):

    driver.get(whoscored_url)

    match_id = extract_match_id_from_url(whoscored_url)
    if not match_id:
        print("No match id found")
        return
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//script[contains(text(), "matchCentreData")]'))
        )
    except:
        print(f'Brak danych w {whoscored_url}')
        return

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    element = soup.select_one('script:-soup-contains("matchCentreData")')
    if not element:
        print(f"Brak elementu do zapisania {whoscored_url}")
        return

    try:
        matchdict = json.loads(element.text.split("matchCentreData: ")[1].split(',\n')[0])
    except Exception as e:
        print(f"Błąd parsowania")
        return

    match_events = matchdict['events']

    df = pd.DataFrame(match_events)

    df['match_id'] = match_id

    df.dropna(subset='playerId', inplace=True)

    df = df.where(pd.notnull(df), None)

    df = df.rename(
    {
        'eventId': 'event_id',
        'expandedMinute': 'expanded_minute',
        'outcomeType': 'outcome_type',
        'isTouch': 'is_touch',
        'playerId': 'player_id',
        'teamId': 'team_id',
        'endX': 'end_x',
        'endY': 'end_y',
        'blockedX': 'blocked_x',
        'blockedY': 'blocked_y',
        'goalMouthZ': 'goal_mouth_z',
        'goalMouthY': 'goal_mouth_y',
        'isShot': 'is_shot',
        'cardType': 'card_type',
        'isGoal': 'is_goal'
    },
        axis = 1
    )


    df['period_display_name'] = df['period'].apply(lambda x: x['displayName'])
    df['type_display_name'] = df['type'].apply(lambda x: x['displayName'])
    df['outcome_display_name'] = df['outcome_type'].apply(lambda x: x['displayName'])

    df.drop(columns=['period', 'type', 'outcome_type'], inplace=True)

    if 'is_goal' not in df.columns:
        df['is_goal'] = False

    if 'is_card' not in df.columns:
        df['is_card'] = False
        df['card_type'] = False

    df = df[~(df['type_display_name'] == "OffsideGiven")]

    df = df[[
        'id', 'event_id', 'minute', 'second', 'team_id', 'player_id', 'x', 'y', 'end_x', 'end_y',
        'is_touch', 'blocked_x', 'blocked_y', 'goal_mouth_z', 'goal_mouth_y', 'is_shot',
        'card_type', 'is_goal', 'type_display_name', 'outcome_display_name',
        'period_display_name', 'match_id', 'qualifiers'
    ]]

    df[['id', 'event_id', 'minute', 'team_id', 'player_id', 'match_id']] = df[['id', 'event_id', 'minute', 'team_id', 'player_id', 'match_id']].astype(int)
    df[['second', 'x', 'y', 'end_x', 'end_y']] = df[['second', 'x', 'y', 'end_x', 'end_y']].astype(float)
    df[['is_shot', 'is_goal', 'card_type']] = df[['is_shot', 'is_goal', 'card_type']].astype(bool)

    df['is_goal'] = df['is_goal'].fillna(False)
    df['is_shot'] = df['is_shot'].fillna(False)

    df_clean = df.replace({np.nan: None})
    events = df_clean.to_dict(orient='records')

    for column in df.columns:
        if df[column].dtype == np.float64 or df[column].dtype == np.float32:
            df[column] = np.where(
                np.isnan(df[column]),
                None,
                df[column]
            )

    insert_match_events(df, supabase)

    team_info = []
    team_info.append({
        'team_id': matchdict['home']['teamId'],
        'name': matchdict['home']['name'],
        'country_name': matchdict['home']['countryName'],
        'manager_name': matchdict['home']['managerName'],
        'players': matchdict['home']['players']
    })

    team_info.append({
        'team_id': matchdict['away']['teamId'],
        'name': matchdict['away']['name'],
        'country_name': matchdict['away']['countryName'],
        'manager_name': matchdict['away']['managerName'],
        'players': matchdict['away']['players']
    })

    insert_players(team_info, supabase)

    insert_teams(team_info, supabase)

    return print('Success')

driver.get("https://www.whoscored.com/teams/65/fixtures/spain-barcelona")
time.sleep(3)

soup = BeautifulSoup(driver.page_source, 'html.parser')

all_urls = soup.select('a[href*="\/live\/"]')

all_urls = list(set([
    'https://www.whoscored.com' + x.attrs['href']
    for x in all_urls
]))

print(all_urls)

for url in all_urls:
    print(url)
    scrape_match_events(
        whoscored_url=url,
        driver=driver
    )

    time.sleep(5)
driver.quit()