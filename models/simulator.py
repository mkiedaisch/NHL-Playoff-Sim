import random
from models.elo import win_probability, update_elo

def simulate_series(team_a, team_b, elo_dict, home_adv_dict, k=20):
    """Simulates a best-of-7 series between two teams."""
    wins_a = 0
    wins_b = 0
    elo_a = elo_dict[team_a]
    elo_b = elo_dict[team_b]

    # Home-ice order: 2-2-1-1-1
    home_order = [team_a, team_a, team_b, team_b, team_a, team_b, team_a]

    for game in range(7):
        if wins_a == 4 or wins_b == 4:
            break

        home_team = home_order[game]
        away_team = team_b if home_team == team_a else team_a

        home_adv = home_adv_dict.get(home_team, 100)
        prob = win_probability(elo_dict[home_team], elo_dict[away_team], home_advantage=home_adv)
        if random.random() < prob:
            winner = home_team
            loser = away_team
        else:
            winner = away_team
            loser = home_team

        # Update Elo ratings
        expected = win_probability(elo_dict[winner], elo_dict[loser])
        elo_w, elo_l = update_elo(elo_dict[winner], elo_dict[loser], k=k, expected_win=expected)
        elo_dict[winner] = elo_w
        elo_dict[loser] = elo_l

        if winner == team_a:
            wins_a += 1
        else:
            wins_b += 1

    series_winner = team_a if wins_a > wins_b else team_b
    return series_winner, f"{wins_a}-{wins_b}" if series_winner == team_a else f"{wins_b}-{wins_a}"

def simulate_playoffs(bracket, elo_dict, home_adv_dict):
    """Simulates the full 2025 playoff bracket and returns the champion + results by round."""
    results = {"Round 1": [], "Round 2": [], "Conference Finals": [], "Stanley Cup": []}

    # Round 1
    round_1_winners = []
    for matchup in bracket["Round 1"]:
        winner, score = simulate_series(matchup[0], matchup[1], elo_dict, home_adv_dict)
        results["Round 1"].append((matchup[0], matchup[1], winner, score))
        round_1_winners.append(winner)

    # Round 2 (pair up in bracket order)
    round_2_matchups = list(zip(round_1_winners[::2], round_1_winners[1::2]))
    round_2_winners = []
    for matchup in round_2_matchups:
        winner, score = simulate_series(matchup[0], matchup[1], elo_dict, home_adv_dict)
        results["Round 2"].append((matchup[0], matchup[1], winner, score))
        round_2_winners.append(winner)

    # Conference Finals
    east_final = simulate_series(round_2_winners[0], round_2_winners[1], elo_dict, home_adv_dict)
    results["Conference Finals"].append((round_2_winners[0], round_2_winners[1], *east_final))
    west_final = simulate_series(round_2_winners[2], round_2_winners[3], elo_dict, home_adv_dict)
    results["Conference Finals"].append((round_2_winners[2], round_2_winners[3], *west_final))

    # Stanley Cup
    cup_final = simulate_series(east_final[0], west_final[0], elo_dict, home_adv_dict)
    results["Stanley Cup"].append((east_final[0], west_final[0], *cup_final))

    return results, cup_final[0]
