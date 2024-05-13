import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Initialize the data
players = ["Player 1", "Player 2", "Player 3", "Player 4"]
tournaments = []
rankings = pd.DataFrame({"Player": players, "Points": [0]*4})

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
            winner = st.selectbox("Winner", players, key=f"winner_{i}")
            loser = st.selectbox("Loser", [p for p in players if p != winner], key=f"loser_{i}")
            score_winner = st.number_input("Score Winner:", min_value=0, max_value=10, value=6)
            score_loser = st.number_input("Score Loser:", min_value=0, max_value=10, value=4)
            tournament_results.append(((winner, loser), (score_winner, score_loser)))
        submitted = st.form_submit_button("Submit")
        if submitted:
            return tournament_results
    return None

# Function to calculate the rank
def calculate_rank(tournament_results):
    wins = {player: 0 for player in players}
    games_won = {player: 0 for player in players}
    for ((winner, loser), (score_winner, score_loser)) in tournament_results:
        wins[winner] += 1
        games_won[winner] += score_winner
        games_won[loser] += score_loser
    rankings = sorted(players, key=lambda x: (-wins[x], -games_won[x]))
    points = [10, 6, 4, 2]
    for i, player in enumerate(rankings):
        rankings.loc[rankings["Player"] == player, "Points"] += points[i]

# Function to record the results and update the rank
def record_results(tournament_results):
    tournaments.append(tournament_results)
    calculate_rank(tournament_results)

# Main app
st.write("Edit player names:")
edit_player_names()

st.write("Enter the results of a new tournament:")
tournament_results = enter_tournament_results()
if tournament_results:
    record_results(tournament_results)

# Display the current rank
st.write("Current Rank:")
st.write(rankings.sort_values("Points", ascending=False))

# Plot the rank
st.write("Rank over time:")
fig, ax = plt.subplots()
for i in range(4):
    player_points = [rankings.loc[rankings["Player"] == players[i], "Points"].values[0] for _ in range(len(tournaments))]
    ax.plot(range(len(tournaments)), player_points, label=players[i])
ax.set_xlabel("Tournament")
ax.set_ylabel("Points")
ax.set_title("Rank over time")
ax.legend()
st.pyplot(fig)
