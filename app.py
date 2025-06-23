import streamlit as st
import pandas as pd
import random
from PIL import Image
import os

# === CONFIG ===
NUM_SIMULATIONS = 1000
TEAMS = [
    "carolina_hurricanes", "colorado_avalanche", "dallas_stars", "edmonton_oilers",
    "florida_panthers", "los_angeles_kings", "minnesota_wild", "montreal_canadiens",
    "new_jersey_devils", "ottawa_senators", "st_louis_blues", "tampa_bay_lightning",
    "toronto_maple_leafs", "vegas_golden_knights", "washington_capitals", "winnipeg_jets"
]
TEAM_NAMES = {team: team.replace("_", " ").title() for team in TEAMS}
LOGO_PATH = "assets/logos"

# === ELO RATINGS ===
elo_ratings = {team: random.randint(1400, 1800) for team in TEAMS}

# === FUNCTION TO LOAD LOGO ===
def load_logo(team_key):
    path = os.path.join(LOGO_PATH, f"{team_key}.png")
    try:
        return Image.open(path)
    except:
        return None

# === MATCHUP SIMULATION ===
def simulate_series(team1, team2):
    elo1, elo2 = elo_ratings[team1], elo_ratings[team2]
    p1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
    wins = {team1: 0, team2: 0}
    while wins[team1] < 4 and wins[team2] < 4:
        winner = team1 if random.random() < p1 else team2
        wins[winner] += 1
    return team1 if wins[team1] == 4 else team2, wins[team1], wins[team2]

# === BRACKET SIMULATION ===
def simulate_bracket():
    round1 = [
        ("winnipeg_jets", "st_louis_blues"),
        ("dallas_stars", "colorado_avalanche"),
        ("vegas_golden_knights", "minnesota_wild"),
        ("los_angeles_kings", "edmonton_oilers"),
        ("toronto_maple_leafs", "ottawa_senators"),
        ("florida_panthers", "tampa_bay_lightning"),
        ("washington_capitals", "montreal_canadiens"),
        ("new_jersey_devils", "carolina_hurricanes"),
    ]
    results = {"R1": [], "R2": [], "R3": [], "Final": []}

    # Round 1
    r2_teams = []
    for t1, t2 in round1:
        winner, w1, w2 = simulate_series(t1, t2)
        results["R1"].append((t1, t2, winner, w1, w2))
        r2_teams.append(winner)

    # Round 2
    r3_teams = []
    for i in range(0, len(r2_teams), 2):
        t1, t2 = r2_teams[i], r2_teams[i+1]
        winner, w1, w2 = simulate_series(t1, t2)
        results["R2"].append((t1, t2, winner, w1, w2))
        r3_teams.append(winner)

    # Conference Finals
    finalists = []
    for i in range(0, len(r3_teams), 2):
        t1, t2 = r3_teams[i], r3_teams[i+1]
        winner, w1, w2 = simulate_series(t1, t2)
        results["R3"].append((t1, t2, winner, w1, w2))
        finalists.append(winner)

    # Stanley Cup Final
    t1, t2 = finalists
    winner, w1, w2 = simulate_series(t1, t2)
    results["Final"].append((t1, t2, winner, w1, w2))

    return results, winner

# === MAIN APP ===
st.set_page_config("NHL Playoff Simulator", layout="wide")
st.title("🏒 2025 NHL Playoff Simulator")
st.caption("Simulates the Stanley Cup Playoffs using Elo + Monte Carlo. Select a team, run the sim, and view the bracket!")

# === Sidebar Controls ===
user_pick = st.sidebar.selectbox("Which team do you think will win the Cup?", [TEAM_NAMES[t] for t in TEAMS])
user_key = [k for k, v in TEAM_NAMES.items() if v == user_pick][0]

if st.sidebar.button("Run Simulation"):
    # === Run 1000 Simulations ===
    st.subheader("📉 Stanley Cup Win Percentages (1000 Simulations)")
    win_counter = {team: 0 for team in TEAMS}
    for _ in range(NUM_SIMULATIONS):
        _, champ = simulate_bracket()
        win_counter[champ] += 1

    df = pd.DataFrame.from_dict(win_counter, orient='index', columns=["Cup Wins"])
    df["Win %"] = (df["Cup Wins"] / NUM_SIMULATIONS * 100).round(2)
    df = df.sort_values("Win %", ascending=False)
    df.index = [TEAM_NAMES[i] for i in df.index]

    st.dataframe(df.style.highlight_rows(lambda x: x.name == user_pick, color="lightgreen"))

if st.sidebar.button("Run Single Bracket Simulation"):
    st.subheader("🧊 Simulated Bracket (One Sample Run)")
    sim_result, champion = simulate_bracket()

    for round_name in ["R1", "R2", "R3", "Final"]:
        st.markdown(f"### {round_name.replace('R', 'Round ')}")
        for t1, t2, winner, w1, w2 in sim_result[round_name]:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                logo1 = load_logo(t1)
                if logo1: st.image(logo1, width=60)
            with col2:
                st.markdown(f"**{TEAM_NAMES[t1]}** vs **{TEAM_NAMES[t2]}** — *{w1}-{w2}* → **{TEAM_NAMES[winner]}** advances")
            with col3:
                logo2 = load_logo(t2)
                if logo2: st.image(logo2, width=60)

    st.success(f"🏆 **{TEAM_NAMES[champion]}** wins the Stanley Cup!")
