import streamlit as st
import os
from utils.data_loader import load_team_data
from utils.analysis import run_monte_carlo
from models.simulator import simulate_playoffs
import plotly.graph_objects as go

# Round 1 matchups (East/West, 2025 structure)
round_1 = [
    ("Toronto Maple Leafs", "Ottawa Senators"),
    ("Tampa Bay Lightning", "Florida Panthers"),
    ("Washington Capitals", "Montreal Canadiens"),
    ("Carolina Hurricanes", "New Jersey Devils"),
    ("Vegas Golden Knights", "Minnesota Wild"),
    ("Los Angeles Kings", "Edmonton Oilers"),
    ("Winnipeg Jets", "St. Louis Blues"),
    ("Dallas Stars", "Colorado Avalanche"),
]

bracket_info = {"Round 1": round_1}

# --- Page Config ---
st.set_page_config(page_title="2025 NHL Playoff Simulator", layout="wide")
st.title("🏆 2025 NHL Playoff Simulator")
st.markdown("Simulates the Stanley Cup Playoffs using Elo + Monte Carlo. Select a team, run the sim, and view the bracket!")

# --- Load data ---
elo_dict, home_adv_dict, team_list = load_team_data()

# --- Sidebar ---
user_pick = st.sidebar.selectbox("Which team do you think will win the Cup?", team_list)
run_button = st.sidebar.button("Run Simulation")

# --- Helper for logos ---
def get_logo(team):
    for ext in ("png", "jpg", "jpeg"):
        path = os.path.join("assets/logos", f"{team}.{ext}")
        if os.path.exists(path):
            return path
    txt = os.path.join("assets/logos", f"{team}.txt")
    return txt if os.path.exists(txt) else None

# --- Bracket plot ---
def draw_bracket(results):
    fig = go.Figure()
    dx, dy = 300, 120
    rounds = ["Round 1", "Round 2", "Conference Finals", "Stanley Cup"]
    
    for i, rnd in enumerate(rounds):
        fig.add_annotation(x=i*dx, y=dy*4 + 40, text=rnd, showarrow=False)

    for rnd_idx, rnd in enumerate(rounds):
        matches = results.get(rnd, [])
        for j, match in enumerate(matches):
            a, b, winner, score = match
            x = rnd_idx*dx
            y = dy*4 - j*dy*2
            fig.add_annotation(x=x, y=y, text=f"{a} vs {b}", showarrow=False)
            fig.add_annotation(x=x, y=y-30, text=f"🏅 {winner} ({score})", showarrow=False, font_color="green")

    fig.update_layout(width=dx*len(rounds)+100, height=dy*9, margin=dict(l=10,r=10,t=50,b=50))
    st.plotly_chart(fig, use_container_width=True)

# --- Run simulation ---
if run_button:
    st.subheader("🏒 Stanley Cup Win Percentages (1000 Simulations)")
    win_df = run_monte_carlo(bracket_info, n=1000)

    for _, row in win_df.iterrows():
        team = row.Team
        pct = row["Win %"]
        col1, col2 = st.columns([1,8])
        logo = get_logo(team)
        with col1:
            if logo:
                st.image(logo, width=40)
        with col2:
            st.write(f"**{team}** — {pct}% chance")

    # --- Highlight user prediction ---
    match_row = win_df[win_df["Team"].str.lower() == user_pick.lower()]
    if not match_row.empty:
        pct = match_row["Win %"].values[0]
        st.success(f"✅ Your pick ({user_pick}) won the Cup in {pct}% of simulations.")
    else:
        st.error(f"❌ Your pick ({user_pick}) did not win any of the simulations.")

    # --- Simulate one bracket to visualize ---
    st.markdown("---")
    st.subheader("🧊 Sample Bracket (One Simulation Run)")
    sim_elo = elo_dict.copy()
    sim_home = home_adv_dict.copy()
    sample_results, champ = simulate_playoffs(bracket_info, sim_elo, sim_home)

    # Optional debug: see simulation structure
    st.caption("Bracket structure (debug):")
    st.json(sample_results)

    draw_bracket(sample_results)