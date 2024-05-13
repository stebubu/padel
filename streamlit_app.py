import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os


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

if 'rankings_df' not in st.session_state:
    st.session_state.rankings_df = pd.DataFrame(initial_data)



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


def record_results(tournament_results):
    # Increment tournament played count for all players
    st.session_state.rankings_df['Tournaments Played'] += 1

    # Process each tournament result
    for result in tournament_results:
        ((team1_player1, team1_player2), (team2_player1, team2_player2), (score_team1, score_team2)) = result
        
        # Update matches and games statistics
        if score_team1 > score_team2:
            # Team 1 Wins
            for player in [team1_player1, team1_player2]:
                st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Matches Won'] += 1
                st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Games Won'] += score_team1
                st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Games Lost'] += score_team2
            # Team 2 Loses
            for player in [team2_player1, team2_player2]:
                st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Matches Lost'] += 1
                st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Games Won'] += score_team2
                st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Games Lost'] += score_team1
        else:
            # Similar logic for team 2 winning

    # Calculate points and update ranks, tournaments won etc.
    calculate_rank(tournament_results)

def calculate_rank(tournament_results):
    # Current logic for updating Points and determining who won the tournament
    # Now also calculate 'Ratio Points/Tournaments'
    for player in players:
        row = st.session_state.rankings_df[st.session_state.rankings_df['Player'] == player]
        if row['Tournaments Played'].item() > 0:
            ratio = row['Points'].item() / row['Tournaments Played'].item()
            st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Ratio Points/Tournaments'] = ratio

    # Update CSV and rankings view after changes
    st.session_state.rankings_df.to_csv("data.csv", index=False)












'''# Function to calculate the rank
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
        st.session_state.rankings_df.loc[st.session_state.rankings_df['Player'] == player, 'Points'] += points_distribution[idx]

    st.session_state.rankings_df.sort_values("Points", ascending=False, inplace=True)

# Function to record the results and update the rank
def record_results(tournament_results):
    tournaments.append(tournament_results)
    calculate_rank(tournament_results)
    # Save to CSV if needed
    st.session_state.rankings_df.to_csv("data.csv", index=False)'''

# Main app
st.write("Edit player names:")
edit_player_names()

st.write("Enter the results of a new tournament:")
tournament_results = enter_tournament_results()
if tournament_results:
    record_results(tournament_results)

# Display the current rank

st.write("Current Rank:")
st.dataframe(st.session_state.rankings_df.sort_values("Points", ascending=False))


'''# Display the updated rankings table
st.write("Current Rank:")
st.dataframe(st.session_state.rankings_df)
'''

