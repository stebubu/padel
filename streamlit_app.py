import streamlit as st
import pandas as pd
import os
from io import BytesIO
import xlsxwriter

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

# Function to reset the rankings
def reset_rankings():
    # Clear the DataFrame
    st.session_state.rankings = pd.DataFrame(columns=['Player', 'Total Points', 'Tournaments', 'Sets Won', 'Games Won', 'Games Lost'])
    # Optionally, delete the CSV file
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
    st.success("Rankings have been reset.")
    st.experimental_rerun()  # Refresh the app to update the display


def get_excel_download_link(df):
    """Generates a download link allowing the data in a given panda dataframe to be downloaded as an Excel file."""
    towrite = BytesIO()  # create a BytesIO object
    # Write DataFrame to an Excel buffer
    with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    towrite.seek(0)  # Rewind the buffer
    # Create a download button and return it
    return st.download_button(label="Download Excel file", data=towrite.read(), file_name='tournament_rankings.xlsx', mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

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


def finalize_rankings(tournament_players):
    if 'rankings' in st.session_state and not st.session_state.rankings.empty:
        # Filter the DataFrame to include only players from the current tournament
        tournament_rankings = st.session_state.rankings[st.session_state.rankings['Player'].isin(tournament_players)].copy()

        # Calculate game difference for sorting and resolving ties
        tournament_rankings['Game Difference'] = tournament_rankings['Games Won'] - tournament_rankings['Games Lost']
        tournament_rankings.sort_values(['Sets Won', 'Game Difference'], ascending=[False, False], inplace=True)

        # Assign points based on tournament rankings
        points_distribution = [10, 6, 4, 2] + [0] * (len(tournament_rankings) - 4)
        last_points_awarded = None
        last_index = 0

        for i in range(len(tournament_rankings)):
            if i == 0 or (tournament_rankings.iloc[i]['Sets Won'] != tournament_rankings.iloc[i-1]['Sets Won'] or
                          tournament_rankings.iloc[i]['Game Difference'] != tournament_rankings.iloc[i-1]['Game Difference']):
                # Assign points from the distribution
                points_to_assign = points_distribution[min(i, len(points_distribution)-1)]
            else:
                # Tie, assign the same as last assigned
                points_to_assign = last_points_awarded

            # Update the main DataFrame
            player_name = tournament_rankings.iloc[i]['Player']
            player_index = st.session_state.rankings[st.session_state.rankings['Player'] == player_name].index
            st.session_state.rankings.loc[player_index, 'Total Points'] += points_to_assign
            st.session_state.rankings.loc[player_index, 'Tournaments'] += 1

            last_points_awarded = points_to_assign

        # Save updates and remove temporary columns
        save_rankings_to_csv()

def main():
    st.title('CIRCOLO PADEL RIMINI - MERCOLEDI DA LEONI')

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

    if st.button("AGGIORNA TAPPA"):
        tournament_players = [players[0],players[1],players[2],players[3]]  # Example list
        finalize_rankings(tournament_players)


    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))


    # Provide download link for Excel file
    get_excel_download_link(st.session_state.rankings)

    # Placement for the reset button
    if st.button('Reset Rankings'):
        reset_rankings()


if __name__ == "__main__":
    main()


