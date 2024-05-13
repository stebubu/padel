import streamlit as st
import pandas as pd

# Initialize the DataFrame for rankings if it doesn't exist
if 'rankings' not in st.session_state:
    st.session_state.rankings = pd.DataFrame(columns=['Player', 'Total Points', 'Tournaments', 'Sets Won', 'Games Won', 'Games Lost'])

# Helper function to update ranking based on each match
def update_games(player_name, games_won, games_lost):
    if player_name in st.session_state.rankings['Player'].values:
        player_data = st.session_state.rankings[st.session_state.rankings['Player'] == player_name]
        idx = player_data.index[0]
        st.session_state.rankings.loc[idx, 'Games Won'] += games_won
        st.session_state.rankings.loc[idx, 'Games Lost'] += games_lost
    else:
        new_data = pd.DataFrame({
            'Player': [player_name],
            'Total Points': [0],
            'Tournaments': [0],
            'Sets Won': [0],
            'Games Won': [games_won],
            'Games Lost': [games_lost]
        })
        st.session_state.rankings = pd.concat([st.session_state.rankings, new_data], ignore_index=True)

# Helper function to finalize rankings after a tournament
def finalize_rankings():
    # Sorting by Sets Won and then by game difference
    st.session_state.rankings['Game Difference'] = st.session_state.rankings['Games Won'] - st.session_state.rankings['Games Lost']
    st.session_state.rankings.sort_values(['Sets Won', 'Game Difference'], ascending=[False, False], inplace=True)
    points_distribution = [10, 6, 4, 2]  # Points for 1st, 2nd, 3rd, and 4th
    for idx, points in zip(st.session_state.rankings.index, points_distribution):
        st.session_state.rankings.loc[idx, 'Total Points'] += points
        st.session_state.rankings.loc[idx, 'Tournaments'] += 1
    st.session_state.rankings.drop(columns=['Game Difference'], inplace=True)

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
                    for team, games in games_won.items():
                        players_team = team.split('/')
                        for player in players_team:
                            update_games(player, games, 0 if games == 12 else 12-games)
                    st.success(f"Results recorded for {match[0]} vs {match[1]}")

    # Step 3: Update Rankings
    if st.button("Finalize Tournament"):
        finalize_rankings()
        st.write("Rankings updated successfully!")

    # Step 4: Display Rankings
    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))

if __name__ == "__main__":
    main()


