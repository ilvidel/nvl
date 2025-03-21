import csv
from collections import Counter
from itertools import count

import igraph as ig
import matplotlib.pyplot as plt
import pandas
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
import statistics

from game import Game
from seasons import total_games


class MyPlotter:

    def __init__(self):
        self.games = []
        with open("past.csv", "r") as csv_file:
            csv_games = csv.DictReader(csv_file)
            for g in csv_games:
                self.games.append(Game.from_csv(g))

        self.dataframe = pandas.read_csv("past.csv")

        self.referee_subset = [
            # "Aileen Barry",
            # "Alistair Mitchell",
            # "Ben Hill",
            # "Daniel Sarnik",
            # "Fiona Cotterill",
            # "Francesca Bentley",
            # "Giordano Machi",
            # "Ignacio Diez",
            # "Jacky Pang",
            # "Janet Leach",
            # "Jayne Jones",
            # "Mel Melville-brown",
            # "Neil Bentley",
            # "Nick Heckford",
            # "Peter Parsons",
            # "Richard Burbedge",
            "Richard Parkes",
            # "Rita Grimes",
            "Roberto Rigante",
            # "Su Brennand",
            # "Timothy Hebborn",
            # "William Perugini",
        ]

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
            if total < 75:  # this result is wrong and should be ignored
                print(game.csv())
                continue
            if game.home_sets == '2' and game.away_sets == '2':
                # Apparently, games cancelled because of COVID were, for some reason,
                # entered in the system with impossible results in the form:
                # Home: 2 - 23 25 23 25 15
                # Away: 2 - 25 23 25 23 15
                print(game.csv())
                continue
            points.append(total)
            sex.append(game.category)

        print(f"MAX: {max(points)}")
        print(f"MIN: {min(points)}")
        print(f"AVG: {int(statistics.mean(points))}")
        print(f"Median: {statistics.median(points)}")
        print(f"Mode: {statistics.mode(points)}")

        df = pandas.DataFrame(dict(points=points, gender=sex))
        fig = px.histogram(
            df, x="points", color="gender",
            color_discrete_sequence=['hotpink', 'dodgerblue'],
            opacity=.5,
            # nbins=300,
            marginal="rug",  # can be `box`, `violin` or 'rug'
            title="Total points played per game")
        fig.update_layout(barmode='group')  # stack, group, overlay or relative
        fig.show()

    def plot_points_histogram(self):
        """
        Histogram of the total number of points per game, per number of sets
        (the sum of home points and away points)
        """
        points = []
        sets = []

        for game in self.games:
            total = sum(
                [int(x) for x in game.home_points + game.away_points if x.isnumeric()])
            if total < 75:  # this result is wrong and should be ignored
                continue
            if game.home_sets == '2' and game.away_sets == '2':
                continue
            points.append(total)
            sets.append(f"{int(game.home_sets) + int(game.away_sets)} sets")

        df = pandas.DataFrame(dict(points=points, sets=sets))
        fig = px.histogram(
            df, x="points", color="sets",
            # color_discrete_sequence=['hotpink', 'dodgerblue'],
            opacity=.7,
            marginal="rug",  # can be `box`, `violin` or 'rug'
            nbins=300,
            title="Total points played per game")
        fig.update_layout(barmode='stack')  # stack, group, overlay or relative
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
        divs = ['superleague', 'division_1', 'division_2', 'division_3', 'cup', 'shield']
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
        """Number of games played per season"""
        seasons = [g.season for g in self.games]
        fig = px.histogram(seasons, title="Number of games per season")
        fig.update_layout(bargap=.2)
        fig.show()

    def plot_number_of_games_per_division(self):
        """Number of games played per season, per division"""
        series = []
        seasons = set(self.dataframe['season'])

        for the_season in sorted(seasons):
            games = self.dataframe[self.dataframe['season'] == the_season]
            count = Counter(games['division'])
            series.append([
                the_season,
                count['superleague'],
                count['division_1'],
                count['division_2'],
                count['division_3'],
                count['cup'],
                count['shield'],
            ])

        df = pandas.DataFrame(
            series,
            columns=['Season', 'Superleague', 'Div1', 'Div2', 'Div3', 'Cup', 'Shield']
        )
        fig = px.bar(
            df,
            x='Season', y=['Superleague', 'Div1', 'Div2', 'Div3', 'Cup', 'Shield'],
            title="Number of games per division, per year",
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.show()

    def plot_games_per_division_percentage(self):
        series = []
        seasons = set(self.dataframe['season'])

        for the_season in sorted(seasons):
            games = self.dataframe[self.dataframe['season'] == the_season]
            count = Counter(games['division'])
            total_games = len(games)
            series.append([
                the_season,
                count['superleague'] / total_games,
                count['division_1'] / total_games,
                count['division_2'] / total_games,
                count['division_3'] / total_games,
                count['cup'] / total_games,
                count['shield'] / total_games,
            ])

        df = pandas.DataFrame(
            series,
            columns=['Season', 'Superleague', 'Div1', 'Div2', 'Div3', 'Cup', 'Shield']
        )
        fig = px.bar(
            df,
            x='Season', y=['Superleague', 'Div1', 'Div2', 'Div3', 'Cup', 'Shield'],
            title="Percentage of games per division, per year",
            labels='Division',
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.show()

    def plot_number_of_teams_per_division(self):
        """Number of games played per season, per division"""
        series = []
        seasons = set(self.dataframe['season'])
        divisions = ['superleague', 'division_1', 'division_2', 'division_3', 'cup', 'shield']
        for the_season in sorted(seasons):
            count = []
            for div in divisions:
                games = self.dataframe[self.dataframe['season'] == the_season]
                division = games[games['division'] == div]
                count.append(len(set(division['home']).union(set(division['away']))))
            series.append([the_season] + count)

        df = pandas.DataFrame(
            series,
            columns=['Season', 'Superleague', 'Div1', 'Div2', 'Div3', 'Cup', 'Shield']
        )
        fig = px.bar(
            df,
            x='Season', y=['Superleague', 'Div1', 'Div2', 'Div3', 'Cup', 'Shield'],
            title="Number of Teams per Divison, per year",
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
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
        # where one team has 0 total points. Or add them as sections.
        # They skew the result and I think it's an outlier
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

    def plot_number_of_teams(self):
        """Plot number of teams per year"""
        count = {}
        for g in self.games:
            if g.division == 'playoffs': continue
            year = g.timestamp.year
            if year not in count: count[year] = {
                'superleague': set(),
                'division_1': set(),
                'division_2': set(),
                'division_3': set(),
                'cup': set(),
                'shield': set(),
            }
            count[year][g.division].add(g.home)
            count[year][g.division].add(g.away)

        # df = pandas.DataFrame(dict(
        #     years=count.keys(),
        #     divisions=['superleague', 'division_1', 'division_2', 'division_3', 'cup', 'shield'],
        #     count=count.values()
        # ))
        fig = px.bar(count)
        fig.show()

    def plot_total_games_per_referee(self):
        """Bar chart of the total number of games per referee"""
        from collections import Counter
        refs = []
        for g in self.games:
            if g.r2 and not g.r2.isnumeric() and not g.r2 == 'TBC':
                refs.append(g.r2)
            if g.r1 and not g.r1.isnumeric() and not g.r1 == 'TBC':
                refs.append(g.r1)

        c = Counter(refs)

        df = pandas.DataFrame(
            dict(refs=c.keys(), count=c.values())
        )

        fig = px.bar(
            df,
            y='refs',
            x='count',
            title="Games per referee",
            color='count',
            color_continuous_scale='rdbu',
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending', 'title': 'Referee'},
            xaxis={'title': 'Number of Games'}
        )

        fig.show()

    def plot_games_per_referee_per_season(self):
        """
        Interactive bar chart, showing the number of games
        that a particular referee has officiated each season
        """
        # Extract relevant data from Game objects
        game_data = [(game.timestamp.year, game.division, game.r1, game.r2) for game in self.games]
        df = pandas.DataFrame(game_data, columns=['Year', 'Division', 'R1', 'R2'])
        # df['Year'] = pandas.to_datetime(df['Date']).dt.year

        referees = set(df['R1']).union(set(df['R2']))

        dropdown_buttons = []
        fig = go.Figure()

        for referee in sorted(referees):
            ref_games = df[(df['R1'] == referee) | (df['R2'] == referee)]
            grouped_data = ref_games.groupby(['Year', 'Division']).size().unstack(fill_value=0)

            traces = []
            for division in grouped_data.columns:
                traces.append(go.Bar(
                    x=grouped_data.index,
                    y=grouped_data[division],
                    name=division,
                    visible=False
                ))

            dropdown_buttons.append({
                'label': referee,
                'method': 'update',
                'args': [
                    {'visible': [True if i // len(grouped_data.columns) == list(referees).index(referee) else False
                                 for i in range(len(referees) * len(grouped_data.columns))]},
                    {'title.text': f'Games Officiated by {referee} Per Year'}
                ]
            })

            fig.add_traces(traces)

        fig.update_layout(
            title=f'Games Officiated by {list(referees)[0]} Per Year',
            xaxis_title='Year',
            yaxis_title='Number of Games',
            barmode='stack',
            updatemenus=[{
                'buttons': dropdown_buttons,
                'direction': 'down',
                'showactive': True
            }]
        )

        fig.show()

    def plot_referees_per_year(self):
        """Plot total number of referees per year"""
        # years = [g.timestamp.year for g in self.games]
        count = {}
        for g in self.games:
            div = g.division
            r1 = g.r1
            r2 = g.r2

            if not r1 and not r2: continue

            y = g.timestamp.year
            if y not in count: count[y] = {}
            if div not in count[y]: count[y][div] = set()
            if r1: count[y][div].add(r1)
            if r2: count[y][div].add(r2)

        years, divs, refs = [], [], []
        for y in count:
            for d in count[y]:
                years.append(str(y))
                divs.append(d)
                refs.append(str(len(count[y][d])))

        df = pandas.DataFrame(dict(
            years=years,
            divisions=divs,
            refs=refs
        ))
        fig = px.histogram(df, x='years', y='refs', color='divisions', hover_data='refs', title="Number of Referees")
        fig.show()

    """
    def plot_holoviews(self):
        import pandas as pd
        import holoviews as hv
        from holoviews import opts, dim
        from bokeh.sampledata.les_mis import data

        hv.extension('bokeh')
        hv.output(size=200)

        links = pd.DataFrame(data['links'])
        hv.Chord(links)
        nodes = hv.Dataset(pd.DataFrame(data['nodes']), 'index')
        nodes.data.head()
        chord = hv.Chord((links, nodes)).select(value=(5, None))
        chord.opts(
            opts.Chord(cmap='Category20', edge_cmap='Category20', edge_color=dim('source').str(),
                       labels='name', node_color=dim('index').str()))

    def plot_openchord(self):
        import openchord as ocd

        adjacency_matrix = [[3, 18, 9, 0, 23],
                            [18, 0, 12, 5, 29],
                            [9, 12, 0, 27, 10],
                            [0, 5, 27, 0, 0],
                            [23, 29, 10, 0, 0]]
        labels = ['Emma', 'Isabella', 'Ava', 'Olivia', 'Sophia']

        fig = ocd.Chord(adjacency_matrix, labels)
        fig.colormap = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880',
                        '#FF97FF', '#FECB52']
        fig.show()
        fig.save_svg("figure.svg")
    """

    def generate_community_graph(self):
        # Extract edges between Home and Away teams
        edges = list(zip(self.dataframe['Home'], self.dataframe['Away']))

        # Create a graph from the edge list
        g = ig.Graph.TupleList(edges, directed=False)

        # Detect communities
        # communities = g.community_multilevel()
        communities = g.community_edge_betweenness()
        communities = communities.as_clustering()

        # colorize communities
        num_communities = len(communities)
        palette = ig.RainbowPalette(n=num_communities)
        for i, community in enumerate(communities):
            g.vs[community]["color"] = i
            community_edges = g.es.select(_within=community)
            community_edges["color"] = i

        # Assign community membership to vertices
        g.vs['community'] = communities.membership

        # Plot the graph with communities
        layout = g.layout('fr', niter=5000)
        ig.plot(
            communities,
            layout=layout,
            palette=palette,
            vertex_label=g.vs['name'],
            vertex_label_size=6,
            vertex_size=5,
            vertex_color=[f"#{c:06x}" for c in g.vs['community']],
            bbox=(1920, 1080),  # Increase the size of the plot
            margin=50,  # Add margin to reduce clutter at the edges
            target="/tmp/communities_teams.pdf"
        )

    def generate_connected_components_graph(self):
        # Extract edges between Home and Away teams
        good_edges = []
        edges = list(zip(self.dataframe['R1'], self.dataframe['R2']))
        print(len(edges))

        bad = ["TBC", 119979, 116921, 119791, "119979", "116921", "119791"]
        good = ["Ignacio Diez", "Jayne Jones", "Richard Burbedge", "Neil Bentley",
                "Francesca Bentley",
                "Alistair Mitchell",
                "Nick Heckford",
                "Timothy Hebborn",
                "Peter Parsons",
                "Su Brennand",
                "Janet Leach",
                "Jacky Pang",
                "Richard Parkes",
                "Fiona Cotterill",
                "Ben Hill",
                "William Perugini",
                "Rita Grimes",
                "Aileen Barry",
                "Alessia Garnero",
                "Daniel Sarnik",
                "Mel Melville-brown",
                ]
        for t in edges:
            if any([type(x) is int for x in t]):
                print(f"Removing: {t}")
                continue
            elif any([type(x) is float for x in t]):
                print(f"Removing: {t}")
                continue
            elif any([x in bad for x in t]):
                print(f"Removing: {t}")
                continue
            # if t[0] in good and t[1] in good:
            good_edges.append(t)
        print(len(good_edges))

        # Create a graph from the edge list
        g = ig.Graph.TupleList(good_edges, directed=True)

        # generate communities
        communities = g.community_edge_betweenness()

        # convert into a vertex clustering
        communities = communities.as_clustering()

        # print who belongs where
        for j, community in enumerate(communities):
            print(f"Community {j}:")
            for v in community:
                g.vs["label"] = g.vs["name"]
                print(f"\t{g.vs[v].index} {g.vs[v]['name']}")

        # colorize communities
        num_communities = len(communities)
        palette = ig.RainbowPalette(n=num_communities)
        for j, community in enumerate(communities):
            g.vs[community]["color"] = j
            community_edges = g.es.select(_within=community)
            community_edges["color"] = j

        # plot
        fig1, ax1 = plt.subplots()
        ig.plot(
            communities,
            layout="kk",
            target=ax1,
            palette=palette,
            mark_groups=True,
            vertex_size=15,
            vertex_label_dist=3,
            edge_width=0.5,
        )
        fig1.set_size_inches(20, 20)
        fig1.savefig("teams.pdf")

    def plot_observations(self):
        """Number of games played per year, per division"""
        count = {}
        names = [
            # "Aileen Barry",
            # "Ana Pal",
            # "Fiona Cotterill",
            # "Stephen Watts",
            # "Giorgio Scatigna-Gianfagna",
            # "Elia Gironacci",
            # "Cherie Cheung",
            # "Rita Grimes",
            # "Nicolas Vecchione",
            # "Domitilla Di Stefano",
            "Ignacio Diez", "Nick Heckford", "Diane Hollows", "Glynn Archibald", "Lenny Barry", "Debra Smart"
        ]
        division_name = {
            'Division 1 Men': "Div1",
            'Division 1 Women': "Div1",
            'Division 2 Central Men': "Div2",
            'Division 2 East Women': "Div2",
            'Division 2 North Men': "Div2",
            'Division 2 North Women': "Div2",
            'Division 2 South Men': "Div2",
            'Division 2 West Women': "Div2",
            'Division 3 Central Women': "Div3",
            'Division 3 North Central Men': "Div3",
            'Division 3 North West Men': "Div3",
            'Division 3 North Women': "Div3",
            'Division 3 South East Men': "Div3",
            'Division 3 South West Men': "Div3",
            'Division 3 South West Women': "Div3",
            'Division 3 South East Women': "Div3",
            'Super League Men': "SuperLeague",
            'Super League Women': "SuperLeague"
        }

        for g in self.games:
            div = division_name[g.division]
            if g.r1 in names:
                if div not in count: count[div] = []
                count[div].append(g.r1)
            if g.r2 in names:
                if div not in count: count[div] = []
                count[div].append(g.r2)

        print(count.keys())

        fig = go.Figure()
        # for i in set(division_name.values()):
        #     fig.add_trace(go.Histogram(x=count[i], name=i))
        fig.add_trace(go.Histogram(x=count["Div3"], name="Div3"))
        fig.add_trace(go.Histogram(x=count["Div2"], name="Div2"))
        fig.add_trace(go.Histogram(x=count["Div1"], name="Div1"))
        fig.add_trace(go.Histogram(x=count["SuperLeague"], name="SuperLeague"))
        fig.update_layout(
            barmode='stack',
            bargap=.2,
            xaxis_title_text='Referee',  # xaxis label
            yaxis_title_text='Number of Games',  # yaxis label
            title="Number of games per referee, per division")
        fig.show()

    def referee_network(self):
        bad = ["TBC", 119979, 116921, 119791, "119979", "116921", "119791", ""]

        edges = {}
        vertices = set()
        for g in self.games:
            if g.r1 in bad or g.r2 in bad: continue

            # comment this out to get a reduced set of refs
            # if g.r1 not in good or g.r2 not in good: continue

            if g.r1 not in edges:
                edges[g.r1] = {}
            if g.r2 not in edges[g.r1]:
                edges[g.r1][g.r2] = 0
            vertices.add(g.r1)
            vertices.add(g.r2)
            edges[g.r1][g.r2] += 1
        return edges, list(vertices)

    def plot_referee_network(self, directed=False):
        ref_matrix, refs = self.referee_network()
        g = ig.Graph(directed=directed)
        g.add_vertices(refs)

        for r1 in ref_matrix:
            for r2, w in ref_matrix[r1].items():
                g.add_edge(r1, r2, weight=w)

        # Detect communities
        communities = g.community_edge_betweenness(directed=directed)
        communities = communities.as_clustering()
        # Assign community membership to vertices
        g.vs['community'] = communities.membership

        # colorize
        num_communities = len(communities)
        palette = ig.RainbowPalette(n=num_communities)
        for i, community in enumerate(communities):
            g.vs[community]["color"] = i
            community_edges = g.es.select(_within=community)
            community_edges["color"] = i

        ig.plot(
            communities,
            layout='dh',
            bbox=(1920, 1080),  # Increase the size of the plot,
            edge_label=g.es['weight'],
            edge_label_color=g.es['color'],
            edge_width=g.es['weight'],
            margin=100,  # Add margin to reduce clutter at the edges,
            mark_groups=True,
            palette=palette,
            target="referee_network_communities.png",
            vertex_label=g.vs['name'],
            vertex_label_dist=2,
            # vertex_label_size=10,
            # vertex_size=10,
        )

    def teams_network(self):
        bad = ["TBC"]
        good = []
        edges = {}
        vertices = set()
        for g in self.games:
            if g.home in bad or g.away in bad: continue

            # comment this out to get a reduced set of refs
            # if g.r1 not in good or g.r2 not in good: continue

            if g.home not in edges:
                edges[g.home] = {}
            if g.away not in edges[g.home]:
                edges[g.home][g.away] = 0
            vertices.add(g.home)
            vertices.add(g.away)
            edges[g.home][g.away] += 1
        return edges, list(vertices)

    def plot_teams_network(self):
        team_matrix, teams = self.teams_network()
        g = ig.Graph(directed=False)
        g.add_vertices(teams)

        for home in team_matrix:
            for away, w in team_matrix[home].items():
                g.add_edge(home, away, weight=w)

        # Detect communities
        communities = g.community_edge_betweenness(directed=False)
        communities = communities.as_clustering()
        # Assign community membership to vertices
        g.vs['community'] = communities.membership

        # colorize
        num_communities = len(communities)
        palette = ig.RainbowPalette(n=num_communities)
        for i, community in enumerate(communities):
            g.vs[community]["color"] = i
            community_edges = g.es.select(_within=community)
            community_edges["color"] = i

        ig.plot(
            communities,
            layout='dh',
            bbox=(1920, 1080),  # Increase the size of the plot,
            # edge_label=g.es['weight'],
            # edge_label_color=g.es['color'],
            # edge_width=g.es['weight'],
            margin=100,  # Add margin to reduce clutter at the edges,
            mark_groups=True,
            palette=palette,
            target="referee_team_communities.png",
            vertex_label=g.vs['name'],
            vertex_label_dist=2,
            # vertex_label_size=10,
            # vertex_size=10,
        )

    def plot_referee_role(self, ref_name):
        """Plot the number of R1 vs R2 roles for a particular referee"""
        r1 = len(list(filter(lambda g: g.r1 == ref_name, self.games)))
        r2 = len(list(filter(lambda g: g.r2 == ref_name, self.games)))
        both = len(list(filter(lambda g: g.r1 == ref_name and g.r2 == ref_name, self.games)))

        donut_colors = ["#26547C", "#EF476F", "#FFD166", "#06D6A0"]
        labels = ["Ref1", "Ref2", "Both"]
        values = [r1, r2, both]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            direction='clockwise',
            sort=False,  # do not sort by value
            hole=0.5,
            title=f"Roles for {ref_name}"
        )])
        fig.update_traces(
            textinfo="label+percent+value",
            marker=dict(colors=donut_colors)
        )
        fig.show()

    def plot_referee_games_by_division(self, ref_name):
        """Plot the number of games by a particular referee, per division"""
        # TODO: split by category as well, in similar color shade
        games = list(filter(lambda g: g.r1 == ref_name or g.r2 == ref_name, self.games))
        sl = len(list(filter(lambda g: "Super" in g.division, games)))
        div1 = len(list(filter(lambda g: "Division 1" in g.division, games)))
        div2 = len(list(filter(lambda g: "Division 2" in g.division, games)))
        div3 = len(list(filter(lambda g: "Division 3" in g.division, games)))

        donut_colors = ["#26547C", "#EF476F", "#FFD166", "#06D6A0"]
        labels = ["SuperLeague", "Div1", "Div2", "Div3"]
        values = [sl, div1, div2, div3]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            sort=False,  # do not sort by value
            hole=0.5,
            title=f"Number of Games {ref_name}"
        )])
        fig.update_traces(
            textinfo="label+percent+value",
            marker=dict(colors=donut_colors)
        )
        fig.show()

    def plot_referee_games_by_category(self, ref_name):
        """Plot the number of games by a particular referee, per division"""
        games = list(filter(lambda g: g.r1 == ref_name or g.r2 == ref_name, self.games))
        men = len(list(filter(lambda g: "men" == g.category, games)))
        ladies = len(list(filter(lambda g: "women" == g.category, games)))

        donut_colors = ["#26547C", "#EF476F", "#FFD166", "#06D6A0"]
        labels = ["Men", "Ladies"]
        values = [men, ladies]
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            sort=False,  # do not sort by value
            hole=0.5,
            title=f"Number of Games by {ref_name}"
        )])
        fig.update_traces(
            textinfo="label+percent+value",
            marker=dict(colors=donut_colors)
        )
        fig.show()

    def plot_referee_games_by_team(self, ref_name):
        games = list(filter(lambda g: g.r1 == ref_name or g.r2 == ref_name, self.games))
        teams = []
        for g in games:
            teams.append(f"{g.home} ({g.division})")
            teams.append(f"{g.away} ({g.division})")

        import collections
        c = collections.Counter(teams)
        df = pandas.DataFrame(dict(teams=c.keys(), count=c.values()))
        fig = px.bar(
            df,
            y='teams', x='count',
            color='count',
            title=f"Teams for {ref_name}",
            color_continuous_scale=px.colors.sequential.solar,
            orientation='h'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending', 'title': 'Teams'},
            xaxis={'title': 'Times refereed'}
        )
        fig.show()

    def plot_teams_games_by_referee(self, team_name):
        # TODO: esto es una movida porque por ejemplo,
        #  City of Bristol se llama igual en hombres que en mujeres.
        #  Igual para otros equipos (p.ej. Bristol)
        games = list(filter(lambda g: g.home == team_name or g.away == team_name, self.games))
        refs = []
        for g in games:
            refs.append(f"{g.r1} ({g.category})")
            refs.append(f"{g.r2} ({g.category})")

        import collections
        c = collections.Counter(refs)
        df = pandas.DataFrame(dict(refs=c.keys(), count=c.values()))
        fig = px.bar(
            df,
            y='refs', x='count',
            color='count',
            title=f"Referees for {team_name}",
            color_continuous_scale=px.colors.sequential.Viridis,
            orientation='h'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending', 'title': 'Referees'},
            xaxis={'title': 'Times refereed'}
        )
        fig.show()

    def plot_referee_games_by_venue(self):
        """Bar chart of venues where a referee has officiated"""
        # Extract all referees
        referee_venues = [(game.r1, game.r2, game.venue) for game in self.games]
        all_referees = {ref for match in referee_venues for ref in match[:2] if ref}

        # Count co-occurrences
        co_occurrence = {ref: Counter() for ref in all_referees}
        for ref1, ref2, venue in referee_venues:
            if ref1:
                co_occurrence[ref1][venue] += 1
            if ref2:
                co_occurrence[ref2][venue] += 1

        # Generate initial data (first referee in list as default)
        first_ref = list(sorted(all_referees)).pop()
        referees = list(co_occurrence[first_ref].keys())
        venues = list(co_occurrence[first_ref].values())

        # Create figure
        fig = go.Figure()
        # fig.add_trace(go.Bar(
        #     x=referees,
        #     y=venues,
        #     name=first_ref,
        #     marker=dict(color=venues, colorscale=px.colors.sequential.Viridis)
        # ))
        fig.add_trace(go.Pie(
            labels=referees, values=venues, name=first_ref,
            marker=dict(colors=px.colors.qualitative.Safe),
            hole=0.5
        ))

        # Create dropdown menu
        dropdown_buttons = []
        for ref in sorted(all_referees):
            dropdown_buttons.append({
                'label': ref,
                'method': 'update',
                'args': [
                    {'labels': [list(co_occurrence[ref].keys())],
                     'values': [list(co_occurrence[ref].values())]},
                    {'title.text': f'Where has {ref} Officiated?'}
                ]
            })

        fig.update_traces(textinfo='label+percent+value')
        fig.update_layout(
            # xaxis_title='Refereed at',
            # yaxis_title='Number of games',
            # xaxis={'categoryorder': 'total descending'},
            updatemenus=[{
                'buttons': dropdown_buttons,
                'direction': 'down',
                'showactive': True
            }]
        )

        fig.show()

    def plot_referee_pairings_bar(self):
        """
        Generates an interactive bar chart showing the number of
        times a referee has officiated with another referee.
        The chart includes a dropdown menu to select a referee.
        """
        # Extract all referees
        referee_pairs = [(game.r1, game.r2) for game in self.games]
        all_referees = set(ref for pair in referee_pairs for ref in pair)

        # Count co-occurrences
        co_occurrence = {ref: Counter() for ref in all_referees}
        for ref1, ref2 in referee_pairs:
            co_occurrence[ref1][ref2] += 1
            co_occurrence[ref2][ref1] += 1

        # Generate initial data (first referee in list as default)
        first_ref = list(all_referees)[0]
        x_values = list(co_occurrence[first_ref].keys())
        y_values = list(co_occurrence[first_ref].values())

        # Create figure
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            name=first_ref,
            marker=dict(color=y_values, colorscale='viridis')
        ))

        # Create dropdown menu
        dropdown_buttons = []
        for ref in sorted(all_referees):
            dropdown_buttons.append({
                'label': ref,
                'method': 'update',
                'args': [
                    {'x': [list(co_occurrence[ref].keys())],
                     'y': [list(co_occurrence[ref].values())],
                     'marker': [dict(color=list(co_occurrence[ref].values()), colorscale='viridis')]},
                    {'title.text': f'Number of Games Officiated with {ref}'}
                ]
            })

        fig.update_layout(
            title=f'Number of Games Officiated with {first_ref}',
            xaxis_title='Refereed with',
            yaxis_title='Number of Games',
            xaxis={'categoryorder': 'total ascending'},
            updatemenus=[{
                'buttons': dropdown_buttons,
                'direction': 'down',
                'showactive': True
            }]
        )

        fig.show()

    def plot_referee_pairings_pie(self):
        """
        Generates an interactive pie chart showing the number of
        times a referee has officiated with another referee.
        The chart includes a dropdown menu to select a referee.
        """
        # Extract all referees
        referee_pairs = [(game.r1, game.r2) for game in self.games]
        all_referees = set(ref for pair in referee_pairs for ref in pair)
        print("\n".join(sorted(all_referees)))

        # Count co-occurrences
        co_occurrence = {ref: Counter() for ref in all_referees}
        for ref1, ref2 in referee_pairs:
            co_occurrence[ref1][ref2] += 1
            co_occurrence[ref2][ref1] += 1

        # Generate initial data (first referee in list as default)
        first_ref = list(all_referees)[1]
        labels = list(co_occurrence[first_ref].keys())
        values = list(co_occurrence[first_ref].values())

        # Create figure
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=labels, values=values, name=first_ref,
            marker=dict(colors=px.colors.qualitative.Safe),
            sort=True,
            hole=0.5
        ))

        # Create dropdown menu
        dropdown_buttons = []
        for ref in sorted(all_referees):
            dropdown_buttons.append({
                'label': ref,
                'method': 'update',
                'args': [
                    {'labels': [list(co_occurrence[ref].keys())], 'values': [list(co_occurrence[ref].values())]},
                    {'title.text': f'Number of Games Officiated with {ref}'}
                ]
            })

        fig.update_layout(
            title=f'Number of Referee Pairings for {first_ref}',
            updatemenus=[{
                'buttons': dropdown_buttons,
                'direction': 'down',
                'showactive': True
            }]
        )

        fig.show()

    def plot_referee_team_diversity(self):
        """Show the number of different temas each ref has refereed"""
        teams = {}
        for g in self.games:
            if g.r1 not in teams: teams[g.r1] = set()
            if g.r2 not in teams: teams[g.r2] = set()
            teams[g.r1].add(g.home)
            teams[g.r1].add(g.away)
            teams[g.r2].add(g.home)
            teams[g.r2].add(g.away)

        referees = []
        values = []
        for r in teams:
            if not r: continue
            referees.append(r)
            values.append(len(teams[r]))

        df = pandas.DataFrame(dict(referees=referees, count=values))
        fig = px.bar(
            df, x=referees, y=values,
            color=values,
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        fig.update_layout(
            title_text='Number of Teams per Referee',
            xaxis={'title': 'Referees', 'categoryorder': 'total descending'},
            yaxis={'title': 'Number of Teams'},
        )
        fig.show()

    def plot_referee_team_diversity_index(self):
        """
        Calculate a 'diversity index for each referee.
        This is the number of different teams a ref has refereed divided by
        the number of total games that ref has officiated
         """
        teams = {}
        total_games = Counter()
        for g in self.games:
            if g.r1 not in teams: teams[g.r1] = set()
            if g.r2 not in teams: teams[g.r2] = set()
            teams[g.r1].add(g.home)
            teams[g.r1].add(g.away)
            teams[g.r2].add(g.home)
            teams[g.r2].add(g.away)
            total_games[g.r1] += 1
            total_games[g.r2] += 1

        referees = []
        indices = []
        for r in teams:
            if not r: continue
            referees.append(r)
            indices.append(len(teams[r]) / total_games[r])

        df = pandas.DataFrame(dict(referees=referees, indices=indices))
        fig = px.bar(
            df, x=referees, y=indices,
            color=indices,
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        fig.update_layout(
            title_text='Team Diversity Index',
            xaxis={
                'title': 'Referees',
                'categoryorder': 'total descending'
            },
            yaxis={'title': 'Diversity Index'}
        )
        fig.show()


if __name__ == "__main__":
    plotter = MyPlotter()
    # plotter.plot_total_points()
    # plotter.plot_points_histogram()
    # plotter.plot_results()
    # plotter.plot_home_victories()
    # plotter.plot_home_victories_per_division()
    # plotter.plot_number_of_games()
    # plotter.plot_number_of_games_per_division()
    # plotter.plot_games_per_division_percentage()
    plotter.plot_number_of_teams_per_division()
    # plotter.plot_number_of_teams() # fixme: not working yet
    # plotter.plot_total_games_per_referee()
    # plotter.plot_games_per_referee_per_season()
    # plotter.plot_referees_per_year()

    # plotter.generate_community_graph() # fixme: not working yet
    # plotter.generate_connected_components_graph() # fixme: not working yet

    # plotter.plot_referee_network(directed=False)
    # plotter.plot_teams_network()

    # plotter.plot_observations()

    # plotter.plot_holoviews()
    # plotter.plot_openchord()

    # REFEREES - Individual charts
    # for r in plotter.referee_subset: # TODO: change to the full set of referees
    #     plotter.plot_referee_role(r)
    #     plotter.plot_referee_games_by_division(r)
    #     plotter.plot_referee_games_by_category(r)
    #     plotter.plot_referee_games_by_team(r)
    # plotter.plot_referee_pairings_pie()
    # plotter.plot_referee_team_diversity()
    # plotter.plot_referee_team_diversity_index()
    # plotter.plot_referee_games_by_venue()

    # TEAMS
    # teams = set()
    # for g in plotter.games:
    #     teams.add(g.away)
    #     teams.add(g.home)
    # for t in teams:
    #     if 'Bristol' in t:
    #         plotter.plot_teams_games_by_referee(t)
