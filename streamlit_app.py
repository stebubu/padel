import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# Initialize the data
players = ["Player 1", "Player 2", "Player 3", "Player 4"]
tournaments = []
rankings = pd.DataFrame({"Player": players, "Points": [0]*4})
rankings_df = pd.DataFrame({'Player': players, 'Points': [0]*4})

# Load data from file
if os.path.exists("data.csv"):
    rankings = pd.read_csv("data.csv", index_col=0)

# Create the Streamlit app
st.title("Padel Tournament App")

# Function to edit player names
def edit_player_names():
    st.write("Edit player names:")
    for i, player in enumerate(players):
        new_name = st.text_input(f"Player {i+1}:", value=player)
        if new_name:
            players[i] = new_name
    st.write("Players:", players)

# Function to enter the results of a tournament
def enter_tournament_results():
    with st.form("tournament_results"):
        tournament_results = []
        for i in range(3):
            st.write(f"Match {i+1}:")
            team1_player1 = st.selectbox("Team 1 Player 1", players, key=f"team1_player1_{i}")
            team1_player2 = st.selectbox("Team 2 Player 1", [p for p in players if p != team1_player1], key=f"team1_player2_{i}")
            team2_player1 = st.selectbox("Team 2 Player 1", [p for p in players if p not in [team1_player1, team1_player2]], key=f"team2_player1_{i}")
            team2_player2 = st.selectbox("Team 2 Player 2", [p for p in players if p not in [team1_player1, team1_player2, team2_player1]], key=f"team2_player2_{i}")
            score_team1 = st.number_input("Score Team 1:", min_value=0, max_value=10, value=6, key=f"score_team1_{i}")
            score_team2 = st.number_input("Score Team 2:", min_value=0, max_value=10, value=2, key=f"score_team2_{i}")
            tournament_results.append(((team1_player1, team1_player2), (team2_player1, team2_player2), (score_team1, score_team2)))
        submitted = st.form_submit_button("Submit")
        if submitted:
            return tournament_results
    return None

# Function to calculate the rank
def calculate_rank(tournament_results):
    wins = {player: 0 for player in players}
    games_won = {player: 0 for player in players}
    for ((team1_player1, team1_player2), (team2_player1, team2_player2), (score_team1, score_team2)) in tournament_results:
        if score_team1 > score_team2:
            wins[team1_player1] += 1
            wins[team1_player2] += 1
        else:
            wins[team2_player1] += 1
            wins[team2_player2] += 1
        games_won[team1_player1] += score_team1
        games_won[team1_player2] += score_team1
        games_won[team2_player1] += score_team2
        games_won[team2_player2] += score_team2

    # Sorting players first by wins, then by games won
    sorted_players = sorted(players, key=lambda x: (-wins[x], -games_won[x]))
    points_distribution = [10, 6, 4, 2]
    for idx, player in enumerate(sorted_players):
        rankings_df.loc[rankings_df['Player'] == player, 'Points'] += points_distribution[idx]

    rankings_df.sort_values("Points", ascending=False, inplace=True)

# Function to record the results and update the rank
def record_results(tournament_results):
    tournaments.append(tournament_results)
    calculate_rank(tournament_results)
    rankings_df.to_csv("data.csv", index=False)




# Main app
st.write("Edit player names:")
edit_player_names()

st.write("Enter the results of a new tournament:")
tournament_results = enter_tournament_results()
if tournament_results:
    record_results(tournament_results)

# Display the current rank
st.write("Current Rank:")
# Ensure the DataFrame is sorted by 'Points' in descending order before displaying
rankings_df.sort_values('Points', ascending=False, inplace=True)
st.dataframe(rankings_df)  # or st.table(rankings_df)
