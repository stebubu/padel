import streamlit as st
import pandas as pd

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
    st.title('Tennis Doubles Tournament Tracker')

    # Step 1: Register Players
    with st.form("player_registration"):
        players = [st.text_input(f"Player {i+1} Name:") for i in range(4)]
        submitted = st.form_submit_button("Register Players and Generate Matches")
        if submitted and all(players):
            # Generate all unique doubles matches
            matches = [
                (f"{players[0]}/{players[1]}", f"{players[2]}/{players[3]}"),
                (f"{players[0]}/{players[2]}", f"{players[1]}/{players[3]}"),
                (f"{players[0]}/{players[3]}", f"{players[1]}/{players[2]}")
            ]
            st.session_state.matches = matches
            st.session_state.results = {match: {} for match in matches}
            st.success("All doubles matches generated!")

    # Step 2: Collect Match Results
    if 'matches' in st.session_state:
        for match in st.session_state.matches:
            with st.form(f"match_{match[0]}_{match[1]}_results"):
                st.write(f"Match: {match[0]} vs {match[1]}")
                games_won = {
                    match[0]: st.number_input(f"Games won by Team {match[0]}", min_value=0, max_value=12, step=1, key=f"games_{match[0]}"),
                    match[1]: st.number_input(f"Games won by Team {match[1]}", min_value=0, max_value=12, step=1, key=f"games_{match[1]}")
                }
                result_submitted = st.form_submit_button("Submit Result")
                if result_submitted:
                    st.session_state.results[match] = games_won
                    st.success(f"Results recorded for {match[0]} vs {match[1]}")

    # Step 3: Update Rankings
    if st.button("Update Rankings"):
        for match, games in st.session_state.results.items():
            if games:
                team1, team2 = match
                players_team1 = team1.split('/')
                players_team2 = team2.split('/')
                winner_team = team1 if games[team1] > games[team2] else team2
                loser_team = team1 if winner_team == team2 else team2
                winner_points = 10 if games[winner_team] > games[loser_team] else 0
                loser_points = 0
                update_ranking(players_team1[0], winner_points, games[winner_team], games[loser_team])
                update_ranking(players_team1[1], winner_points, games[winner_team], games[loser_team])
                update_ranking(players_team2[0], loser_points, games[loser_team], games[winner_team])
                update_ranking(players_team2[1], loser_points, games[loser_team], games[winner_team])
        st.write("Rankings updated successfully!")

    # Step 4: Display Rankings
    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))

if __name__ == "__main__":
    main()

