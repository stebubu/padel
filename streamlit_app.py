import streamlit as st
import pandas as pd
import os

# Initialize data
players = ["Player 1", "Player 2", "Player 3", "Player 4"]
initial_data = {
    'Player': players,
    'Points': [0]*4,
    'Tournaments Played': [0]*4,
    'Tournaments Won': [0]*4,
    'Matches Won': [0]*4,
    'Matches Lost': [0]*4,
    'Games Won': [0]*4,
    'Games Lost': [0]*4,
    'Ratio Points/Tournaments': [0.0]*4
}

# Initialize or load data
if 'rankings_df' not in st.session_state or not os.path.exists("data.csv"):
    st.session_state.rankings_df = pd.DataFrame(initial_data)
else:
    st.session_state.rankings_df = pd.read_csv("data.csv")

# Streamlit app title
st.title("Padel Tournament App")

# Function to edit player names
def edit_player_names():
    st.write("Edit player names:")
    for i in range(len(players)):
        new_name = st.text_input(f"Player {i+1}:", value=st.session_state.rankings_df['Player'][i])
        if new_name:
            st.session_state.rankings_df.loc[i, 'Player'] = new_name

# Function to enter the results of a tournament
def enter_tournament_results():
    with st.form("tournament_results"):
        tournament_results = []
        for i in range(3):
            st.write(f"Match {i+1}:")
            team1_player1 = st.selectbox("Team 1 Player 1", st.session_state.rankings_df['Player'], key=f"team1_player1_{i}")
            team1_player2 = st.selectbox("Team 1 Player 2", [p for p in st.session_state.rankings_df['Player'] if p != team1_player1], key=f"team1_player2_{i}")
            team2_player1 = st.selectbox("Team 2 Player 1", [p for p in st.session_state.rankings_df['Player'] if p not in [team1_player1, team1_player2]], key=f"team2_player1_{i}")
            team2_player2 = st.selectbox("Team 2 Player 2", [p for p in st.session_state.rankings_df['Player'] if p not in [team1_player1, team1_player2, team2_player1]], key=f"team2_player2_{i}")
            score_team1 = st.number_input("Score Team 1:", min_value=0, max_value=10, value=6, key=f"score_team1_{i}")
            score_team2 = st.number_input("Score Team 2:", min_value=0, max_value=10, value=2, key=f"score_team2_{i}")
            tournament_results.append(((team1_player1, team1_player2), (team2_player1, team2_player2), (score_team1, score_team2)))
        submitted = st.form_submit_button("Submit")
        if submitted:
            return tournament_results
    return None




def calculate_rank(tournament_results):
    # Initialize local dictionaries to track the stats
    wins = {player: 0 for player in players}
    games_won = {player: 0 for player in players}
    matches_won = {player: 0 for player in players}
    matches_lost = {player: 0 for player in players}
    games_lost = {player: 0 for player in players}

    # Process results to update wins, games won, and games lost
    for ((team1_player1, team1_player2), (team2_player1, team2_player2), (score_team1, score_team2)) in tournament_results:
        if score_team1 > score_team2:
            update_team_stats(team1_player1, team1_player2, score_team1, score_team2, True, wins, matches_won, games_won, matches_lost, games_lost)
            update_team_stats(team2_player1, team2_player2, score_team2, score_team1, False, wins, matches_won, games_won, matches_lost, games_lost)
        else:
            update_team_stats(team2_player1, team2_player2, score_team2, score_team1, True, wins, matches_won, games_won, matches_lost, games_lost)
            update_team_stats(team1_player1, team1_player2, score_team1, score_team2, False, wins, matches_won, games_won, matches_lost, games_lost)

    # Apply the computed metrics to the DataFrame
    apply_player_stats(wins, games_won, matches_won, matches_lost, games_lost)

def update_team_stats(player1, player2, games_won_team, games_lost_team, is_winner, wins, matches_won, games_won, matches_lost, games_lost):
    team_players = [player1, player2]
    for player in team_players:
        if is_winner:
            wins[player] += 1
            matches_won[player] += 1
        else:
            matches_lost[player] += 1
        games_won[player] += games_won_team
        games_lost[player] += games_lost_team

def apply_player_stats(wins, games_won, matches_won, matches_lost, games_lost):
    for player in players:
        # Ensure you're correctly referencing the DataFrame and the condition is valid.
        player_mask = st.session_state.rankings_df['Player'] == player
        if player_mask.any():  # Ensures there's at least one match, avoids empty slice operations.
            # Safely update DataFrame by explicitly referencing existing indices and columns.
            st.session_state.rankings_df.loc[player_mask, 'Matches Won'] += matches_won[player]
            st.session_state.rankings_df.loc[player_mask, 'Matches Lost'] += matches_lost[player]
            st.session_state.rankings_df.loc[player_mask, 'Games Won'] += games_won[player]
            st.session_state.rankings_df.loc[player_mask, 'Games Lost'] += games_lost[player]



# Main app
edit_player_names()

st.write("Enter the results of a new tournament:")
tournament_results = enter_tournament_results()
if tournament_results:
    calculate_rank(tournament_results)

st.write("Current Rank:")
st.dataframe(st.session_state.rankings_df.sort_values("Points", ascending=False))



