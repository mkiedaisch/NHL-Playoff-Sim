import streamlit as st
import random
import os
from PIL import Image
import pandas as pd

st.set_page_config(page_title="2025 NHL Playoff Simulator", layout="wide")

# --- Data ---
teams = [
    "winnipeg_jets", "st_louis_blues", "dallas_stars", "colorado_avalanche",
    "vegas_golden_knights", "minnesota_wild", "los_angeles_kings", "edmonton_oilers",
    "toronto_maple_leafs", "ottawa_senators", "florida_panthers", "tampa_bay_lightning",
    "washington_capitals", "montreal_canadiens", "new_jersey_devils", "carolina_hurricanes"
]

elo = {
    team: 1500 + random.randint(-150, 150)
    for team in teams
}

team_names = {
    "winnipeg_jets": "Winnipeg Jets",
    "st_louis_blues": "St. Louis Blues",
    "dallas_stars": "Dallas Stars",
    "colorado_avalanche": "Colorado Avalanche",
    "vegas_golden_knights": "Vegas Golden Knights",
    "minnesota_wild": "Minnesota Wild",
    "los_angeles_kings": "Los Angeles Kings",
    "edmonton_oilers": "Edmonton Oilers",
    "toronto_maple_leafs": "Toronto Maple Leafs",
    "ottawa_senators": "Ottawa Senators",
    "florida_panthers": "Florida Panthers",
    "tampa_bay_lightning": "Tampa Bay Lightning",
    "washington_capitals": "Washington Capitals",
    "montreal_canadiens": "Montreal Canadiens",
    "new_jersey_devils": "New Jersey Devils",
    "carolina_hurricanes": "Carolina Hurricanes"
}

# --- Functions ---
def win_prob(team1, team2):
    rating1 = elo[team1]
    rating2 = elo[team2]
    return 1 / (1 + 10 ** ((rating2 - rating1) / 400))

def simulate_series(team1, team2):
    wins = {team1: 0, team2: 0}
    while wins[team1] < 4 and wins[team2] < 4:
        prob = win_prob(team1, team2)
        winner = team1 if random.random() < prob else team2
        wins[winner] += 1
    return team1 if wins[team1] == 4 else team2, f"{wins[team1]}–{wins[team2]}"

def simulate_bracket():
    round1 = [
        ("winnipeg_jets", "st_louis_blues"),
        ("dallas_stars", "colorado_avalanche"),
        ("vegas_golden_knights", "minnesota_wild"),
        ("los_angeles_kings", "edmonton_oilers"),
        ("toronto_maple_leafs", "ottawa_senators"),
        ("florida_panthers", "tampa_bay_lightning"),
        ("washington_capitals", "montreal_canadiens"),
        ("new_jersey_devils", "carolina_hurricanes")
    ]

    r1_winners = []
    series_scores = []
    for t1, t2 in round1:
        winner, score = simulate_series(t1, t2)
        r1_winners.append(winner)
        series_scores.append((t1, t2, winner, score))

    round2 = [(r1_winners[i], r1_winners[i+1]) for i in range(0, 8, 2)]
    r2_winners = []
    for t1, t2 in round2:
        winner, score = simulate_series(t1, t2)
        r2_winners.append(winner)
        series_scores.append((t1, t2, winner, score))

    round3 = [(r2_winners[0], r2_winners[1]), (r2_winners[2], r2_winners[3])]
    r3_winners = []
    for t1, t2 in round3:
        winner, score = simulate_series(t1, t2)
        r3_winners.append(winner)
        series_scores.append((t1, t2, winner, score))

    final = (r3_winners[0], r3_winners[1])
    champ, score = simulate_series(final[0], final[1])
    series_scores.append((final[0], final[1], champ, score))

    return champ, series_scores

def get_logo(team_id):
    path = f"assets/logos/{team_id}.png"
    if os.path.exists(path):
        return Image.open(path)
    return None

# --- UI ---
st.title("🏆 2025 NHL Playoff Simulator")
st.markdown("Simulates the Stanley Cup Playoffs using Elo + Monte Carlo. Select a team, run the sim, and view the bracket!")

team_pick = st.selectbox("Which team do you think will win the Cup?", [team_names[t] for t in teams])
run_button = st.button("Run Simulation")

if run_button:
    cup_counts = {team: 0 for team in teams}
    all_results = []

    for _ in range(1000):
        champ, _ = simulate_bracket()
        cup_counts[champ] += 1

    st.subheader("📉 Stanley Cup Win Probabilities (1000 Simulations)")
    df = pd.DataFrame([
        {
            "Team": team_names[team],
            "Win %": round(100 * count / 1000, 1)
        } for team, count in sorted(cup_counts.items(), key=lambda x: -x[1])
    ])

    highlight_team = [team for team, name in team_names.items() if name == team_pick][0]
    df_display = df.style.apply(lambda x: ['background-color: lightgreen' if v == team_names[highlight_team] else '' for v in x], subset=['Team'])
    st.dataframe(df_display, use_container_width=True)

    top_team = max(cup_counts, key=cup_counts.get)
    st.success(f"🏆 Most likely Stanley Cup winner: **{team_names[top_team]}** ({round(100 * cup_counts[top_team] / 1000, 1)}%)")

# Single sim
if st.button("Run Single Bracket Simulation"):
    champ, bracket = simulate_bracket()
    st.subheader("🧊 Single Simulation Bracket")

    for round_num in range(1, 5):
        st.markdown(f"### Round {round_num}")
        for match in bracket[(round_num - 1)*4 : round_num*4]:
            t1, t2, winner, score = match
            col1, col2 = st.columns([1, 4])
            with col1:
                logo1 = get_logo(t1)
                logo2 = get_logo(t2)
                if logo1: st.image(logo1, width=50)
                if logo2: st.image(logo2, width=50)
            with col2:
                st.write(f"**{team_names[t1]}** vs **{team_names[t2]}**")
                st.write(f"✅ Winner: **{team_names[winner]}** ({score})")

    st.success(f"🏆 Stanley Cup Champion in this simulation: **{team_names[champ]}**")
