import math

def win_probability(team_elo, opponent_elo, home_advantage=0):
    """Calculate win probability based on Elo ratings and home advantage."""
    adjusted_elo = team_elo + home_advantage
    elo_diff = adjusted_elo - opponent_elo
    return 1 / (1 + 10 ** (-elo_diff / 400))

def update_elo(winner_elo, loser_elo, k=20, expected_win=None):
    """Update Elo ratings after a game."""
    if expected_win is None:
        expected_win = win_probability(winner_elo, loser_elo)
    change = k * (1 - expected_win)
    return winner_elo + change, loser_elo - change
