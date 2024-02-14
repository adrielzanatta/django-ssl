qs = [
    {"id": 13, "winner_team": 0},
    {"id": 14, "winner_team": 2},
    {"id": 15, "winner_team": 2},
    {"id": 16, "winner_team": 1},
]

print([x["winner_team"] for x in qs if x["id"] == 13][0])
