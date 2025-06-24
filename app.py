
import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from PIL import Image
import matplotlib.pyplot as plt

# Setup
st.set_page_config(page_title="🏒 NHL 2025 Playoff Simulator", layout="wide")
st.title("🏒 2025 NHL Playoff Simulator")
st.caption("Simulates full bracket using Elo + Monte Carlo. Includes bracket results, win percentages, Elo trends, and downloadable data.")

# Teams and matchups
first_round = [
    ("Winnipeg Jets", "St. Louis Blues"),
    ("Dallas Stars", "Colorado Avalanche"),
    ("Vegas Golden Knights", "Minnesota Wild"),
    ("Los Angeles Kings", "Edmonton Oilers"),
    ("Toronto Maple Leafs", "Ottawa Senators"),
    ("Florida Panthers", "Tampa Bay Lightning"),
    ("Washington Capitals", "Montreal Canadiens"),
    ("New Jersey Devils", "Carolina Hurricanes"),
]

teams = sorted(set([team for series in first_round for team in series]))
elo = {team: random.randint(1400, 1700) for team in teams}
LOGO_DIR = "assets/logos"

# Helper
def logo_img(team):
    path = os.path.join(LOGO_DIR, team.lower().replace(" ", "_").replace(".", "") + ".png")
    return Image.open(path) if os.path.exists(path) else None

# Simulate a best-of-7 series
def simulate_series(team1, team2, elo_dict):
    elo1, elo2 = elo_dict[team1], elo_dict[team2]
    p1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
    wins1 = wins2 = 0
    while wins1 < 4 and wins2 < 4:
        if random.random() < p1:
            wins1 += 1
        else:
            wins2 += 1
    winner = team1 if wins1 > wins2 else team2
    return winner, (team1, wins1, team2, wins2)

# Full bracket simulation + Elo updates
def simulate_bracket(update_elo=False):
    current_elo = elo.copy()
    rounds = []
    matchups = first_round[:]

    for rnd in range(4):
        results = []
        winners = []
        for t1, t2 in matchups:
            winner, result = simulate_series(t1, t2, current_elo)
            results.append(result)
            winners.append(winner)
            if update_elo:
                change = 25
                current_elo[winner] += change
                current_elo[t1 if t1 != winner else t2] -= change
        rounds.append(results)
        matchups = list(zip(winners[::2], winners[1::2]))
    return rounds, winners[-1], current_elo

# Monte Carlo simulation
def run_monte_carlo(n=1000):
    win_counts = {team: 0 for team in teams}
    elo_tracking = {team: [] for team in teams}
    for _ in range(n):
        _, champ, final_elo = simulate_bracket(update_elo=True)
        win_counts[champ] += 1
        for team in teams:
            elo_tracking[team].append(final_elo[team])
    df = pd.DataFrame.from_dict(win_counts, orient="index", columns=["Cup Wins"])
    df["Win %"] = (df["Cup Wins"] / n * 100).round(2)
    df = df.sort_values("Win %", ascending=False)
    return df, elo_tracking

# UI
user_pick = st.sidebar.selectbox("Which team do you think wins the Cup?", teams)
if st.sidebar.button("Run Simulation"):
    st.session_state["results"], st.session_state["champ"], _ = simulate_bracket()
if st.sidebar.button("Run 1000 Simulations"):
    st.session_state["summary"], st.session_state["elo_series"] = run_monte_carlo()

# Bracket display
if "results" in st.session_state:
    st.subheader("🧊 One Bracket Simulation")
    cols = st.columns(5)
    round_names = ["Round 1", "Round 2", "Conference Finals", "Stanley Cup Final", "🏆 Winner"]

    for i, col in enumerate(cols):
        col.markdown(f"**{round_names[i]}**")
        if i < 4:
            for matchup in st.session_state["results"][i]:
                logo1, logo2 = logo_img(matchup[0]), logo_img(matchup[2])
                if logo1 and logo2:
                    col.image([logo1, logo2], width=50)
                col.caption(f"{matchup[0]} ({matchup[1]}) vs {matchup[2]} ({matchup[3]})")
        else:
            champ = st.session_state["champ"]
            logo = logo_img(champ)
            if logo:
                col.image(logo, width=80)
            col.success(f"{champ} win the Stanley Cup!")

# Monte Carlo results
if "summary" in st.session_state:
    st.subheader("📊 Cup Win Probabilities (1000 Simulations)")
    df = st.session_state["summary"]
    def highlight_team(x):
        return ["background-color: lightgreen" if x.name == user_pick else "" for _ in x]
    st.dataframe(df.style.apply(highlight_team, axis=1), height=500)

    st.download_button("📥 Download Simulation Data", df.to_csv().encode("utf-8"), "cup_win_sim.csv", "text/csv")

    st.markdown("#### 🧠 Finance Insight")
    st.info("This Monte Carlo sim uses Elo ratings as dynamic predictive priors. Similar to portfolio value-at-risk (VaR), it models repeated uncertain outcomes over time, providing probabilistic confidence in forecasted champions.")

    st.markdown("#### 📉 Elo Distribution (After 1000 Sims)")
    fig, ax = plt.subplots(figsize=(10, 4))
    for team, elos in st.session_state["elo_series"].items():
        ax.plot(sorted(elos)[-1:], "o", label=team)
    ax.set_ylabel("Final Elo Rating")
    ax.set_xticks([])
    ax.legend(fontsize=7)
    st.pyplot(fig)

    st.markdown("#### 🪄 Cup Win % Histogram")
    fig2, ax2 = plt.subplots()
    ax2.bar(df.index, df["Win %"])
    ax2.set_ylabel("Win %")
    ax2.set_title("Distribution of Stanley Cup Wins Across 1000 Simulations")
    plt.xticks(rotation=90)
    st.pyplot(fig2)
