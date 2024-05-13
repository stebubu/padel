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
    st.title('Tournament Tracker')

    # Step 1: Register Players
    with st.form("player_registration"):
        players = [st.text_input(f"Player {i+1} Name:") for i in range(4)]
        submitted = st.form_submit_button("Register Players and Generate Matches")
        if submitted and all(players):
            # Generate matches
            matches = [(players[0], players[1]), (players[2], players[3]), (players[0], players[2])]
            st.session_state.matches = matches
            st.session_state.results = {match: {} for match in matches}
            st.success("Matches generated!")

    # Step 2: Collect Match Results
    if 'matches' in st.session_state:
        for match in st.session_state.matches:
            with st.form(f"match_{match[0]}_{match[1]}_results"):
                st.write(f"Match: {match[0]} vs {match[1]}")
                win = st.selectbox(f"Winner ({match[0]} vs {match[1]})", options=[match[0], match[1]])
                game_difference = st.slider(f"Game Difference ({match[0]} vs {match[1]})", min_value=1, max_value=10)
                result_submitted = st.form_submit_button("Submit Result")
                if result_submitted:
                    st.session_state.results[match] = {'winner': win, 'game_difference': game_difference}
                    st.success(f"Result recorded for {match[0]} vs {match[1]}")

    # Step 3: Update Rankings
    if st.button("Update Rankings"):
        for match, result in st.session_state.results.items():
            if result:
                winner = result['winner']
                loser = match[0] if match[1] == winner else match[1]
                update_ranking(winner, 10, 1, 0)  # 10 points for a win, 1 game won, 0 lost
                update_ranking(loser, 0, 0, 1)   # 0 points for a loss, 0 games won, 1 lost
        st.write("Rankings updated successfully!")

    # Step 4: Display Rankings
    st.write("Current Rankings:")
    st.table(st.session_state.rankings.sort_values('Total Points', ascending=False))

if __name__ == "__main__":
    main()
