import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import queries

st.title("Match Dashboard")

players_df = queries.get_players()
