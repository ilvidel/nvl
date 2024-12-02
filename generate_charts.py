import statistics

import pandas
import plotly.express as px
import csv

from game import Game


class MyPlotter:

    def __init__(self):
        self.games = []
        with open("past.csv", "r") as csv_file:
            csv_games = csv.DictReader(csv_file)
            for g in csv_games:
                self.games.append(Game.from_csv(g))

    def plot_total_points(self):
        """
        Histogram of the total number of points per game
        (the sum of home points and away points)
        """
        points = []
        sex = []

        for game in self.games:
            total = sum([int(x) for x in game.home_points + game.away_points if x.isnumeric()])
            if total < 75:
                # print(f"Date: {game.date()} Home: {game.home} ({game.home_points}) Away: {game.away} ({game.away_points})")
                continue
            if total > 250:
                print(f"Date: {game.date()} Home: {game.home} ({game.home_points}) Away: {game.away} ({game.away_points})")
            points.append(total)
            sex.append(game.category)

        print(f"MAX: {max(points)}")
        print(f"MIN: {min(points)}")
        print(f"AVG: {statistics.mean(points)}")
        print(f"Median: {statistics.median(points)}")
        print(f"Mode: {statistics.mode(points)}")

        df = pandas.DataFrame(dict(points=points, gender=sex))
        fig = px.histogram(
            df, x="points", color="gender",
            # nbins=100,
            title="Total points played per game")
        fig.update_layout(barmode='overlay')
        fig.update_traces(opacity=0.75)
        fig.show()


if __name__ == "__main__":
    plotter = MyPlotter()
    plotter.plot_total_points()
