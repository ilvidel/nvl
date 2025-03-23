import csv
import sys

with open("past.csv", "r") as csv_file:
    total_games = csv.DictReader(csv_file)
    all_games = list(total_games)

    year = 2005
    while year < 2025:
        season = f"{year}-{year + 1}"
        games = list(filter(lambda g: g['season'] == season, all_games))

        with open(f"season_{season}.csv", "w") as dest_file:
            header = "season,date,time,ID,home,home_sets,home_points,away,away_sets,away_points,division,category,venue,r1,r2".split(",")
            writer = csv.DictWriter(dest_file, header)
            writer.writeheader()
            sorted_games = sorted(games, key=lambda y: y['date'])
            writer.writerows(games)

        year += 1
