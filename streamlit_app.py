import streamlit as st
import pandas as pd
import os

# Path to the CSV file
csv_file_path = 'tournament_rankings.csv'

# Initialize or load the DataFrame for rankings from CSV if it exists
if os.path.exists(csv_file_path):
    st.session_state.rankings = pd.read_csv(csv_file_path)
else:
    st.session_state.rankings = pd.DataFrame(columns=['Player', 'Total Points', 'Tournaments', 'Sets Won', 'Games Won', 'Games Lost'])

# Function to save rankings to CSV
def save_rankings_to_csv():
    st.session_state.rankings.to_csv(csv_file_path, index=False)

# Function to update games and set wins for both winning and losing teams
def update_games(team_win, games_won_win, games_lost_win, team_lose, games_won_lose, games_lost_lose):
    # Update the winning and losing teams
    players_win = team_win.split('/')
    players_lose = team_lose.split('/')
    for player in players_win:
        update_individual_stats(player, games_won_win, games_lost_win, set_win=1)
    for player in players_lose:
        update_individual_stats(player, games_won_lose, games_lost_lose, set_win=0)

def update_individual_stats(player_name, games_won, games_lost, set_win):
    # Update or add player stats
    if player_name in st.session_state.rankings['Player'].values:
        player_data = st.session_state.rankings[st.session_state.rankings['Player'] == player_name]
        idx = player_data.index[0]
        st.session_state.rankings.loc[idx, 'Games Won'] += games_won
        st.session_state.rankings.loc[idx, 'Games Lost'] += games_lost
        st.session_state.rankings.loc[idx, 'Sets Won'] += set_win
    else:
        new_data = pd.DataFrame({
            'Player': [player_name],
            'Total Points': [0],
            'Tournaments': [0],
            'Sets Won': [set_win],
            'Games Won': [games_won],
            'Games Lost': [games_lost]
        })
        st.session_state.rankings = pd.concat([st.session_state.rankings, new_data], ignore_index=True)
    save_rankings_to_csv()

# Function to finalize rankings after a tournament
def finalize_rankings():
    # Update rankings and sort by total points
    st.session_state.rankings['Game Difference'] = st.session_state.rankings['Games Won'] - st.session_state.rankings['Games Lost']
    st.session_state.rankings.sort_values(['Total Points', 'Sets Won', 'Game Difference'], ascending=[False, False, False], inplace=True)
    points_distribution = [10, 6, 4, 2]
    for idx in range(len(st.session_state.rankings)):
        if idx < len(points_distribution):
            st.session_state.rankings.loc[idx, 'Total Points'] += points_distribution[idx]
            st.session_state.rankings.loc[idx, 'Tournaments'] += 1
    st.session_state.rankings.drop(columns=['Game Difference'], inplace=True)
    save_rankings_to_csv()
    st.experimental_rerun()

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
                    winner_team = match[0] if games_won[match[0]] > games_won[match[1]] else match[1]
                    loser_team = match[1] if winner_team == match[0] else match[0]
                    update_games(winner_team, games_won[winner_team], games_won[loser_team], loser_team, games_won[loser_team], games_won[winner_team])
                    st.success(f"Results recorded for {match[0]} vs {match[1]}")

    if st.button("Finalize Tournament"):
        finalize_rankings()

    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))

    # Step 4: Display Rankings
    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))

if __name__ == "__main__":
    main()


