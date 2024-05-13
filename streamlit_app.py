import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Initialize the data
players = ["Player 1", "Player 2", "Player 3", "Player 4"]
tournaments = []
rankings = pd.DataFrame({"Player": players, "Points": [0]*4})

# Create the Streamlit app
st.title("Padel Tournament App")

# Function to enter the results of a tournament
def enter_tournament_results():
    with st.form("tournament_results"):
        tournament_results = []
        for i in range(3):
            st.write(f"Match {i+1}:")
            winner = st.selectbox("Winner", players, key=f"winner_{i}")
            loser = st.selectbox("Loser", [p for p in players if p != winner], key=f"loser_{i}")
            tournament_results.append((winner, loser))
        submitted = st.form_submit_button("Submit")
        if submitted:
            return tournament_results
    return None

# Function to calculate the rank
def calculate_rank(tournament_results):
    wins = {player: 0 for player in players}
    games_won = {player: 0 for player in players}
    for winner, loser in tournament_results:
        wins[winner] += 1
        games_won[winner] += 1
        games_won[loser] += 0
    rankings = sorted(players, key=lambda x: (-wins[x], -games_won[x]))
    points = [10, 6, 4, 2]
    for i, player in enumerate(rankings):
        rankings.loc[rankings["Player"] == player, "Points"] += points[i]

# Function to record the results and update the rank
def record_results(tournament_results):
    tournaments.append(tournament_results)
    calculate_rank(tournament_results)

# Main app
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
ax.plot(range(len(tournaments)), [rankings.loc[i, "Points"] for i in range(4)])
ax.set_xlabel("Tournament")
ax.set_ylabel("Points")
ax.set_title("Rank over time")
st.pyplot(fig)
