import streamlit as st
import pandas as pd
from itertools import combinations

# Initial setup: Define the base DataFrame for rankings
if 'rankings' not in st.session_state:
    st.session_state.rankings = pd.DataFrame(columns=['Player', 'Total Points', 'Tournaments', 'Games Won', 'Games Lost'])

# Helper function to update ranking
def update_ranking(player_name, points, games_won, games_lost):
    if player_name in st.session_state.rankings['Player'].values:
        player_data = st.session_state.rankings[st.session_state.rankings['Player'] == player_name]
        idx = player_data.index[0]
        st.session_state.rankings.loc[idx, 'Total Points'] += points
        st.session_state.rankings.loc[idx, 'Tournaments'] += 1
        st.session_state.rankings.loc[idx, 'Games Won'] += games_won
        st.session_state.rankings.loc[idx, 'Games Lost'] += games_lost
    else:
        new_data = pd.DataFrame({
            'Player': [player_name],
            'Total Points': [points],
            'Tournaments': [1],
            'Games Won': [games_won],
            'Games Lost': [games_lost]
        })
        st.session_state.rankings = pd.concat([st.session_state.rankings, new_data], ignore_index=True)

def main():
    st.title('Tournament Tracker')

    # Step 1: Register Players
    with st.form("player_registration"):
        players = [st.text_input(f"Player {i+1} Name:") for i in range(4)]
        submitted = st.form_submit_button("Register Players and Generate Matches")
        if submitted and all(players):
            # Generate all unique match pairings
            matches = list(combinations(players, 2))
            st.session_state.matches = matches
            st.session_state.results = {match: {} for match in matches}
            st.success("All possible matches generated!")

    # Step 2: Collect Match Results
    if 'matches' in st.session_state:
        for match in st.session_state.matches:
            with st.form(f"match_{match[0]}_{match[1]}_results"):
                st.write(f"Match: {match[0]} vs {match[1]}")
                games_won = {match[0]: st.number_input(f"Games won by {match[0]}", min_value=0, max_value=12, step=1, key=f"games_{match[0]}"),
                             match[1]: st.number_input(f"Games won by {match[1]}", min_value=0, max_value=12, step=1, key=f"games_{match[1]}")}
                result_submitted = st.form_submit_button("Submit Result")
                if result_submitted:
                    st.session_state.results[match] = games_won
                    st.success(f"Results recorded for {match[0]} vs {match[1]}")

    # Step 3: Update Rankings
    if st.button("Update Rankings"):
        for match, games in st.session_state.results.items():
            if games:
                winner = match[0] if games[match[0]] > games[match[1]] else match[1]
                loser = match[0] if winner == match[1] else match[1]
                winner_points = 10 if games[winner] > games[loser] else 0
                loser_points = 0
                update_ranking(winner, winner_points, games[winner], games[loser])
                update_ranking(loser, loser_points, games[loser], games[winner])
        st.write("Rankings updated successfully!")

    # Step 4: Display Rankings
    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))

if __name__ == "__main__":
    main()

