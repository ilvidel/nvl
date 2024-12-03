import csv
import statistics

import pandas
import plotly.express as px

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
            total = sum(
                [int(x) for x in game.home_points + game.away_points if x.isnumeric()])
            if total < 75: # this result is wrong and should be ignored
                print(
                    f"{game.division} {game.category} Date: {game.date()} Home: {game.home} ({game.home_points}) Away: {game.away} ({game.away_points})")
                continue
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
            title="Total points played per game")
        fig.update_layout(barmode='overlay')
        fig.update_traces(opacity=0.75)
        fig.show()

    def plot_home_victories(self):
        """Percentage of home victories vs away victories"""
        results = []
        for g in self.games:
            r = {'home': g.home_sets, 'away': g.away_sets, 'division': g.division,
                 'category': g.category}
            results.append(r)

        # TODO: take into account forfeited games. Add them as two
        # new sections: forfeited away and forfeited home
        home_victories = len(list(filter(lambda g: g['home'] > g['away'], results)))
        away_victories = len(list(filter(lambda g: g['home'] < g['away'], results)))

        df = pandas.DataFrame(dict(
            where=["Home", "Away"],
            count=[home_victories, away_victories]
        ))
        fig = px.pie(
            df, values='count', names='where', title="Home vs Away victories", hole=.5)
        fig.show()

    def plot_home_victories_per_division(self):
        """Percentage of home victories vs away victories"""
        results = []
        for g in self.games:
            r = {'home': g.home_sets, 'away': g.away_sets, 'division': g.division,
                 'category': g.category}
            results.append(r)

        data = []
        divs = ['superleague', 'division_1', 'division_2', 'division_3', 'cup',
                'shield']
        for div in divs:
            total = len(list(filter(lambda f: f['division'] == div, results)))
            home_victories = len(
                list(filter(lambda g: g['home'] > g['away'] and g['division'] == div,
                            results))) / total
            away_victories = 1 - home_victories
            data.extend([home_victories, away_victories])

        df = pandas.DataFrame(dict(
            # there must be a better way to do this
            where=[
                "Home", "Away",
                "Home", "Away",
                "Home", "Away",
                "Home", "Away",
                "Home", "Away",
                "Home", "Away"],
            divisions=[
                "Super", "Super",
                "Div1", "Div1",
                "Div2", "Div2",
                "Div3", "Div3",
                "Cup", "Cup",
                "Shield", "Shield"],
            count=data
        ))
        fig = px.bar(
            df, x='count', y='divisions',
            color='divisions', pattern_shape='where',
            title="Home vs Away victories per division"
        )
        fig.show()

    def plot_number_of_games(self):
        """Number of games played per year"""
        years = [g.timestamp.year for g in self.games]
        fig = px.histogram(years, title="Number of games per year")
        fig.update_layout(bargap=.2)
        fig.show()

    def plot_number_of_games_per_division(self):
        """Number of games played per year, per division"""
        years = [g.timestamp.year for g in self.games]

        for y in years:
            super = [x.division for x in
                     filter(lambda g: g.timestamp.year == y, self.games)]

        df = pandas.DataFrame(dict(count=count, years=years))
        fig = px.bar(
            df, x='years', y='count', color='count',
            color_continuous_scale='sunsetdark',
            title="Number of games per year, per division")
        fig.show()

    def plot_results(self):
        """Plot the percentage of games where the home team wins"""
        results = {
            "3-0": 0,
            "3-1": 0,
            "3-2": 0,
            "0-3": 0,
            "1-3": 0,
            "2-3": 0,
        }

        # TODO: maybe remove the forfeited games (either 3-0 or 0-3)
        # where one team has 0 total points. That skews the percentage
        # and I think it's an outlier
        for game in self.games:
            if game.home_sets == '3':
                if game.away_sets == '0':
                    results["3-0"] += 1
                elif game.away_sets == '1':
                    results["3-1"] += 1
                elif game.away_sets == '2':
                    results["3-2"] += 1
            elif game.away_sets == '3':
                if game.home_sets == '0':
                    results["0-3"] += 1
                elif game.home_sets == '1':
                    results["1-3"] += 1
                elif game.home_sets == '2':
                    results["2-3"] += 1

        df = pandas.DataFrame(dict(
            keys=results.keys(),
            values=results.values()
        ))

        # fig = px.bar(
        #     df,
        #     x='keys',
        #     y='values',
        #     color='keys',
        #     title="Frequency of each possible result",
        # )
        fig = px.pie(
            df,
            values='values',
            names='keys',
            title="Frequency of each possible result",
            hole=.5,
        )
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=20)
        fig.show()
        return fig


if __name__ == "__main__":
    plotter = MyPlotter()
    # plotter.plot_total_points()
    # plotter.plot_home_victories()
    # plotter.plot_home_victories_per_division()
    # plotter.plot_number_of_games()
    plotter.plot_results()
    # plotter.plot_number_of_games_per_division()  # TODO
