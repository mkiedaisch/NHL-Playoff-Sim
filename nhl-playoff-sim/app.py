import streamlit as st
from utils.data_loader import load_team_data
from utils.analysis import run_monte_carlo

# Define the actual 2025 Round 1 bracket matchups
round_1_matchups = [
    # Eastern Conference
    ("Toronto Maple Leafs", "Ottawa Senators"),
    ("Tampa Bay Lightning", "Florida Panthers"),
    ("Washington Capitals", "Montreal Canadiens"),
    ("Carolina Hurricanes", "New Jersey Devils"),
    # Western Conference
    ("Vegas Golden Knights", "Minnesota Wild"),
    ("Los Angeles Kings", "Edmonton Oilers"),
    ("Winnipeg Jets", "St. Louis Blues"),
    ("Dallas Stars", "Colorado Avalanche"),
]

bracket = {"Round 1": round_1_matchups}

# ----------------------- STREAMLIT APP -----------------------

st.set_page_config(page_title="2025 NHL Playoff Simulator", layout="wide")
st.title("2025 NHL Playoff Simulator")
st.markdown("Simulates the Stanley Cup Playoffs using Elo ratings + Monte Carlo simulation.")

# Load team data
elo_dict, home_adv_dict, team_list = load_team_data()

# Sidebar
st.sidebar.header("Your Prediction")
user_pick = st.sidebar.selectbox("Which team do you think will win the Stanley Cup?", team_list)
run_button = st.sidebar.button("Run Simulation")

# Main display
if run_button:
    with st.spinner("Simulating playoffs..."):
        results_df = run_monte_carlo(bracket, n=1000)

    st.subheader("🏒 Cup Win Probabilities (1000 Simulations)")
    st.dataframe(results_df.style.highlight_max(axis=0, color="lightgreen"), use_container_width=True)

    if user_pick in results_df["Team"].values:
        win_pct = results_df.loc[results_df["Team"] == user_pick, "Win %"].values[0]
        if win_pct > 0:
            st.success(f"✅ Your pick ({user_pick}) won the Cup in {win_pct}% of simulations.")
        else:
            st.error(f"❌ Your pick ({user_pick}) did not win in any simulation.")
    else:
        st.warning("Selected team not found in simulation results.")

    st.caption("This simulation uses Elo-based win probabilities with team-specific home-ice advantages.")
