import pandas as pd

def load_team_data(csv_path="data/nhl_2025_data.csv"):
    """Load team data from CSV and return Elo + home advantage dicts."""
    df = pd.read_csv(csv_path)

    # Create Elo dictionary
    elo_dict = {row["Team"]: row["Elo"] for _, row in df.iterrows()}

    # Create custom home advantage boost per team
    home_adv_dict = {}
    for _, row in df.iterrows():
        home_win_pct = row["HomeWins"] / (row["HomeWins"] + row["HomeLosses"] + row["HomeOTL"])
        road_win_pct = row["RoadWins"] / (row["RoadWins"] + row["RoadLosses"] + row["RoadOTL"])
        diff = home_win_pct - road_win_pct
        boost = 100 + int(diff * 100)  # base 100 + adjusted difference
        home_adv_dict[row["Team"]] = max(50, min(150, boost))  # clamp values

    return elo_dict, home_adv_dict, list(df["Team"])
