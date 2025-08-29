import inspect
import statistics
from collections import Counter

import pandas
import plotly.graph_objects as go
from plotly import express as px

from nvl_plotter import NvlPlotter


class HistoryPlotter(NvlPlotter):
    """
    Generate charts from all the data (i.e. 20 years)
    """

    def plot_total_points_by_category(self):
        """
        Histogram of the total number of points per game, by category
        """
        points = []
        sex = []

        for game in self.games:
            total = sum(
                [int(x) for x in game.home_points + game.away_points if x.isnumeric()]
            )
            if total < 75:  # this result is wrong and should be ignored
                # print("Invalid result: ", game.csv())
                continue
            if game.home_sets == "2" and game.away_sets == "2":
                # Apparently, games cancelled because of COVID were, for some reason,
                # entered in the system with impossible results in the form:
                # Home: 2 - 23 25 23 25 15
                # Away: 2 - 25 23 25 23 15
                # print("COVID game:", game.csv())
                continue
            points.append(total)
            sex.append(game.category)

        print(f"MAX: {max(points)}")
        print(f"MIN: {min(points)}")
        print(f"AVG: {int(statistics.mean(points))}")
        print(f"Median: {statistics.median(points)}")
        print(f"Mode: {statistics.mode(points)}")
        print(f"Total games: {len(points)}")

        df = pandas.DataFrame(dict(points=points, gender=sex))
        fig = px.histogram(
            df,
            x="points",
            color="gender",
            color_discrete_sequence=["orange", "yellowgreen"],
            opacity=0.5,
            nbins=300,
            marginal="violin",  # can be `box`, `violin` or 'rug'
            title="Total points per category",
        )
        fig.update_layout(barmode="overlay")  # stack, group, overlay or relative
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_total_points_per_number_of_sets(self):
        """
        Histogram of the total number of points per game, per number of sets
        """
        points = []
        sets = []

        for game in self.games:
            total = sum(
                [int(x) for x in game.home_points + game.away_points if x.isnumeric()]
            )
            if total < 75:  # this result is wrong and should be ignored
                continue
            if game.home_sets == "2" and game.away_sets == "2":
                continue
            points.append(total)
            sets.append(f"{int(game.home_sets) + int(game.away_sets)} sets")

        df = pandas.DataFrame(dict(points=points, sets=sets))
        fig = px.histogram(
            df,
            x="points",
            color="sets",
            opacity=0.7,
            marginal="box",  # can be `box`, `violin` or 'rug'
            nbins=300,
            title="Total points played per number of sets",
        )
        fig.update_layout(barmode="overlay")  # stack, group, overlay or relative
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_home_victories(self):
        """Percentage of home victories vs away victories"""
        results = []
        for g in self.games:
            r = {
                "home": g.home_sets,
                "away": g.away_sets,
                "division": g.division,
                "category": g.category,
            }
            results.append(r)

        # TODO: take into account forfeited games. Add them as two
        # new sections: forfeited away and forfeited home
        home_victories = len(list(filter(lambda g: g["home"] > g["away"], results)))
        away_victories = len(list(filter(lambda g: g["home"] < g["away"], results)))

        df = pandas.DataFrame(
            dict(where=["Home", "Away"], count=[home_victories, away_victories])
        )
        fig = px.pie(
            df, values="count", names="where", title="Home vs Away victories", hole=0.5
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_home_victories_per_division(self):
        """Percentage of home victories vs away victories, by division"""
        results = []
        for g in self.games:
            r = {
                "home": g.home_sets,
                "away": g.away_sets,
                "division": g.division,
                "category": g.category,
            }
            results.append(r)

        data = []
        divs = [
            "superleague",
            "division_1",
            "division_2",
            "division_3",
            "cup",
            "shield",
        ]
        for div in divs:
            total = len(list(filter(lambda f: f["division"] == div, results)))
            home_victories = (
                    len(
                        list(
                            filter(
                                lambda g: g["home"] > g["away"] and g["division"] == div,
                                results,
                            )
                        )
                    )
                    / total
            )
            away_victories = 1 - home_victories
            data.extend([home_victories, away_victories])

        df = pandas.DataFrame(
            dict(
                # there must be a better way to do this
                where=[
                    "Home",
                    "Away",
                    "Home",
                    "Away",
                    "Home",
                    "Away",
                    "Home",
                    "Away",
                    "Home",
                    "Away",
                    "Home",
                    "Away",
                ],
                divisions=[
                    "Super",
                    "Super",
                    "Div1",
                    "Div1",
                    "Div2",
                    "Div2",
                    "Div3",
                    "Div3",
                    "Cup",
                    "Cup",
                    "Shield",
                    "Shield",
                ],
                count=data,
            )
        )
        fig = px.bar(
            df,
            x="count",
            y="divisions",
            color="divisions",
            pattern_shape="where",
            title="Home vs Away victories, per division",
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_number_of_games_per_season(self):
        """Number of games played per season"""
        seasons = [g.season for g in self.games]
        fig = px.histogram(seasons, title="Number of games per season")
        fig.update_layout(bargap=0.2, showlegend=False)
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_number_of_games_per_season_by_division(self):
        """Number of games played per season, per division"""
        series = []
        seasons = set(self.dataframe["season"])

        for the_season in sorted(seasons):
            games = self.dataframe[self.dataframe["season"] == the_season]
            count = Counter(games["division"])
            series.append(
                [
                    the_season,
                    count["superleague"],
                    count["division_1"],
                    count["division_2"],
                    count["division_3"],
                    count["cup"],
                    count["shield"],
                ]
            )

        df = pandas.DataFrame(
            series,
            columns=["Season", "Superleague", "Div1", "Div2", "Div3", "Cup", "Shield"],
        )
        fig = px.bar(
            df,
            x="Season",
            y=["Shield", "Cup", "Div3", "Div2", "Div1", "Superleague"],
            title="Number of games per division, per year",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_number_of_teams_per_season(self):
        """Plot number of teams per year"""
        series = []
        seasons = set(self.dataframe["season"])
        for the_season in sorted(seasons):
            count = []
            games = self.dataframe[self.dataframe["season"] == the_season]
            count.append(len(set(games["home"]).union(set(games["away"]))))
            series.append([the_season] + count)

        df = pandas.DataFrame(series, columns=["Season", "count"])
        fig = px.bar(
            df,
            x="Season",
            y="count",
            title="Number of Teams per year",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_number_of_teams_per_season_by_division(self):
        """Number of teams registered each year, per division"""
        series = []
        seasons = set(self.dataframe["season"])
        divisions = [
            "superleague",
            "division_1",
            "division_2",
            "division_3",
            "cup",
            "shield",
        ]
        for the_season in sorted(seasons):
            count = []
            for div in divisions:
                games = self.dataframe[self.dataframe["season"] == the_season]
                division = games[games["division"] == div]
                count.append(len(set(division["home"]).union(set(division["away"]))))
            series.append([the_season] + count)

        df = pandas.DataFrame(
            series,
            columns=["Season", "Superleague", "Div1", "Div2", "Div3", "Cup", "Shield"],
        )
        fig = px.bar(
            df,
            x="Season",
            y=["Shield", "Cup", "Div3", "Div2", "Div1", "Superleague"],
            title="Number of Teams registered each year, per division",
            barmode="stack",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_frequency_of_results(self):
        """Frequency of each possible result"""
        results = {
            "3-0": 0,
            "3-1": 0,
            "3-2": 0,
            "0-3": 0,
            "1-3": 0,
            "2-3": 0,
        }

        # TODO: maybe remove the forfeited games (either 3-0 or 0-3)
        # where one team has 0 total points. Or add them as sections.
        # They skew the result and I think it's an outlier
        for game in self.games:
            if game.home_sets == "3":
                if game.away_sets == "0":
                    results["3-0"] += 1
                elif game.away_sets == "1":
                    results["3-1"] += 1
                elif game.away_sets == "2":
                    results["3-2"] += 1
            elif game.away_sets == "3":
                if game.home_sets == "0":
                    results["0-3"] += 1
                elif game.home_sets == "1":
                    results["1-3"] += 1
                elif game.home_sets == "2":
                    results["2-3"] += 1

        df = pandas.DataFrame(dict(keys=results.keys(), values=results.values()))

        # fig = px.bar(
        #     df,
        #     x='keys',
        #     y='values',
        #     color='keys',
        #     title="Frequency of each possible result"
        # )
        fig = px.pie(
            df,
            values="values",
            names="keys",
            title="Frequency of each possible result",
            hole=0.5,
        )
        fig.update_traces(
            textposition="inside", textinfo="percent+label", textfont_size=20
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()
        return fig

    def plot_referees_per_year(self):
        """Plot total number of referees per year"""
        # years = [g.timestamp.year for g in self.games]
        count = {}
        for g in self.games:
            div = g.division
            r1 = g.r1
            r2 = g.r2

            if not r1 and not r2:
                continue

            s = g.season
            if s not in count:
                count[s] = {}
            if div not in count[s]:
                count[s][div] = set()
            if r1:
                count[s][div].add(r1)
            if r2:
                count[s][div].add(r2)

        years, divs, refs = [], [], []
        for s in count:
            for d in count[s]:
                years.append(str(s))
                divs.append(d)
                refs.append(str(len(count[s][d])))

        df = pandas.DataFrame(dict(years=years, divisions=divs, refs=refs))
        fig = px.histogram(
            df,
            x="years",
            y="refs",
            color="divisions",
            hover_data=["refs"],
            title="Number of Referees",
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    # todo: plot referees per year by division

    # def _referee_network(self):
    #     bad = ["TBC", 119979, 116921, 119791, "119979", "116921", "119791", ""]
    #
    #     edges = {}
    #     vertices = set()
    #     for g in self.games:
    #         if g.r1 in bad or g.r2 in bad: continue
    #
    #         # comment this out to get a reduced set of refs
    #         # if g.r1 not in good or g.r2 not in good: continue
    #
    #         if g.r1 not in edges:
    #             edges[g.r1] = {}
    #         if g.r2 not in edges[g.r1]:
    #             edges[g.r1][g.r2] = 0
    #         vertices.add(g.r1)
    #         vertices.add(g.r2)
    #         edges[g.r1][g.r2] += 1
    #     return edges, list(vertices)
    #
    # def plot_referee_network(self, directed=False):
    #     ref_matrix, refs = self._referee_network()
    #     g = ig.Graph(directed=directed)
    #     g.add_vertices(refs)
    #
    #     for r1 in ref_matrix:
    #         for r2, w in ref_matrix[r1].items():
    #             g.add_edge(r1, r2, weight=w)
    #
    #     # Detect communities
    #     communities = g.community_edge_betweenness(directed=directed)
    #     communities = communities.as_clustering()
    #     # Assign community membership to vertices
    #     g.vs['community'] = communities.membership
    #
    #     # colorize
    #     num_communities = len(communities)
    #     palette = ig.RainbowPalette(n=num_communities)
    #     for i, community in enumerate(communities):
    #         g.vs[community]["color"] = i
    #         community_edges = g.es.select(_within=community)
    #         community_edges["color"] = i
    #
    #     ig.plot(
    #         communities,
    #         layout='dh',
    #         bbox=(1920, 1080),  # Increase the size of the plot,
    #         edge_label=g.es['weight'],
    #         edge_label_color=g.es['color'],
    #         edge_width=g.es['weight'],
    #         margin=100,  # Add margin to reduce clutter at the edges,
    #         mark_groups=True,
    #         palette=palette,
    #         target="referee_network_communities.png",
    #         vertex_label=g.vs['name'],
    #         vertex_label_dist=2,
    #         # vertex_label_size=10,
    #         # vertex_size=10,
    #     )

    # def teams_network(self):
    #     bad = ["TBC"]
    #     good = []
    #     edges = {}
    #     vertices = set()
    #     for g in self.games:
    #         if g.home in bad or g.away in bad: continue
    #
    #         # comment this out to get a reduced set of refs
    #         # if g.r1 not in good or g.r2 not in good: continue
    #
    #         if g.home not in edges:
    #             edges[g.home] = {}
    #         if g.away not in edges[g.home]:
    #             edges[g.home][g.away] = 0
    #         vertices.add(g.home)
    #         vertices.add(g.away)
    #         edges[g.home][g.away] += 1
    #     return edges, list(vertices)
    #
    # def plot_teams_network(self):
    #     team_matrix, teams = self.teams_network()
    #     g = ig.Graph(directed=False)
    #     g.add_vertices(teams)
    #
    #     for home in team_matrix:
    #         for away, w in team_matrix[home].items():
    #             g.add_edge(home, away, weight=w)
    #
    #     # Detect communities
    #     communities = g.community_edge_betweenness(directed=False)
    #     communities = communities.as_clustering()
    #     # Assign community membership to vertices
    #     g.vs['community'] = communities.membership
    #
    #     # colorize
    #     num_communities = len(communities)
    #     palette = ig.RainbowPalette(n=num_communities)
    #     for i, community in enumerate(communities):
    #         g.vs[community]["color"] = i
    #         community_edges = g.es.select(_within=community)
    #         community_edges["color"] = i
    #
    #     ig.plot(
    #         communities,
    #         layout='dh',
    #         bbox=(1920, 1080),  # Increase the size of the plot,
    #         # edge_label=g.es['weight'],
    #         # edge_label_color=g.es['color'],
    #         # edge_width=g.es['weight'],
    #         margin=100,  # Add margin to reduce clutter at the edges,
    #         mark_groups=True,
    #         palette=palette,
    #         target="referee_team_communities.png",
    #         vertex_label=g.vs['name'],
    #         vertex_label_dist=2,
    #         # vertex_label_size=10,
    #         # vertex_size=10,
    #     )

    def create_referee_treemap(self):
        """
        Creates a treemap chart showing how many games each referee has officiated,
        with a dropdown to select which season to display.
        """

        # Get all unique seasons for dropdown
        seasons = sorted(list(set(game.season for game in self.games)))

        # Function to get referee counts for a specific season
        def get_referee_counts(season):
            referee_counts = Counter()

            for game in self.games:
                if game.season == season:
                    # Count both r1 and r2 referees
                    if game.r1 and game.r1 != 'unknown':  # Check if r1 is not empty
                        referee_counts[game.r1] += 1
                    if game.r2 and game.r2 != 'unknown':  # Check if r2 is not empty
                        referee_counts[game.r2] += 1

            return referee_counts

        # Create initial treemap for first season
        initial_season = seasons[0] if seasons else None
        if not initial_season:
            # Return empty figure if no seasons found
            fig = go.Figure()
            fig.update_layout(title="No data available")
            return

        initial_counts = get_referee_counts(initial_season)

        # Prepare data for treemap
        referees = list(initial_counts.keys())
        games_count = list(initial_counts.values())

        # Create treemap using go.Treemap for better control
        fig = go.Figure(go.Treemap(
            labels=referees,
            values=games_count,
            marker_colorscale='balance',
            parents=[''] * len(referees)  # All items are top-level
        ))
        fig.update_layout(title=f'Games Officiated by Referees - Season {initial_season}')

        # Create dropdown buttons for all seasons
        dropdown_buttons = []
        for season in seasons:
            season_counts = get_referee_counts(season)
            season_referees = list(season_counts.keys())
            season_games = list(season_counts.values())

            if not season_counts:
                continue

            dropdown_buttons.append({
                'label': f'Season {season}',
                'method': 'restyle',
                'args': [{
                    'labels': [season_referees],
                    'values': [season_games],
                    'parents': [[''] * len(season_referees)]
                }]
            })

        # Update layout with dropdown
        fig.update_layout(
            updatemenus=[{
                'buttons': dropdown_buttons,
                'direction': 'down',
                'showactive': True,
                'x': 0.1,
                'y': 1.15,
                'xanchor': 'left',
                'yanchor': 'top'
            }],
            title={
                'text': f'Games Officiated by Referees - Season {initial_season}',
                'x': 0.5,
                'xanchor': 'center'
            },
            margin=dict(t=100)  # Add top margin for dropdown
        )

        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()
