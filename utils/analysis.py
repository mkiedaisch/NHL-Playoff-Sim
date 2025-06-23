import pandas as pd
from collections import defaultdict
from models.simulator import simulate_playoffs
from utils.data_loader import load_team_data
import copy

def run_monte_carlo(bracket, n=1000):
    """Run many playoff simulations and collect win counts."""
    elo_dict, home_adv_dict, _ = load_team_data()
    win_counter = defaultdict(int)
    all_runs = []

    for _ in range(n):
        sim_elo = copy.deepcopy(elo_dict)
        sim_home = copy.deepcopy(home_adv_dict)
        results, champ = simulate_playoffs(bracket, sim_elo, sim_home)
        win_counter[champ] += 1
        all_runs.append(results)

    win_df = pd.DataFrame({
        "Team": list(win_counter.keys()),
        "Cup Wins": list(win_counter.values()),
    }).sort_values("Cup Wins", ascending=False).reset_index(drop=True)

    win_df["Win %"] = (win_df["Cup Wins"] / n * 100).round(2)
    return win_df
