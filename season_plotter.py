import inspect
from collections import Counter

import pandas
from plotly import express as px
import igraph as ig
from history_plotter import HistoryPlotter
import matplotlib.pyplot as plt

from nvl import HtmlGameParser


class SeasonPlotter(HistoryPlotter):
    """Generate charts for a particular season"""

    # def plot_total_games_per_referee(self):
    #     """Bar chart of the total number of games per referee"""
    #     from collections import Counter
    #
    #     refs = []
    #     for g in self.games:
    #         if g.r2 and not g.r2.isnumeric() and not g.r2 == "TBC":
    #             refs.append(g.r2)
    #         if g.r1 and not g.r1.isnumeric() and not g.r1 == "TBC":
    #             refs.append(g.r1)
    #
    #     c = Counter(refs)
    #
    #     df = pandas.DataFrame(dict(refs=c.keys(), count=c.values()))
    #
    #     fig = px.bar(
    #         df,
    #         y="count",
    #         x="refs",
    #         title="Games per referee",
    #         color="count",
    #         color_continuous_scale="rdbu",
    #     )
    #     fig.update_layout(
    #         xaxis={"categoryorder": "total descending", "title": "Referee"},
    #         yaxis={"title": "Number of Games"},
    #     )
    #
    # if self.publish:
    #     fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
    # else:
    #     fig.show()

    def plot_total_games_per_referee(self):
        """Bar chart of the total number of games per referee"""
        from collections import Counter

        subset = {
            "Abdul Salam Safadi": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Adrian Chan": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Alexandru Calin": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Alex Iftime": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Alex Pavkov": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Aliaksandr Siarheyeu": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Amy Dimmock": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Ana Pal": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Andres Hernandez": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Anna Justkowska": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Bee Yusuf": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Boriss Bovkuns": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Carl Padayachee": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Cherie Cheung": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Cheryl Whittles": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Chon Lam Ieong": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Chris Tsui": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Daniel Harrison": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Daniel Sarnik": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Daryl Carrott": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "David Gardner": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "David Topacho": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Dickson Yiu": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Domitilla Di Stefano": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Edward Arnott": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Elia Gironacci": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Farid Yousof-Nejad": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Fiona Cotterill": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Francesca Bentley": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Francesca Hossain": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Gianni Sutton": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Giordano Marchi": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Giulia Bellan": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Heiner Alzate": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Herman Prada": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Hiroko Turner": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Huaxi Liu": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Ian Hetheringon": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Ignacio Diez": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Igors Maksimovs": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "James Cole": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Jayne Jones": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "John Boughton": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "John Wycliffe": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Kirat Thorat": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Lauren Jingyi Goh": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Lenny Barry": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Ludwik Kowalewski": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Maddie Vararu": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Man Chung Ng": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Martin Mierzwa": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Milan Hak": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Nicolas Vecchione": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Pete Whyard": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Peter Parsons": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Rachel Duerden": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Rita Grimes": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Rommel Medenilla": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Ruben Duarte": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Sam Yip": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Sarah Hanrahan": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Sebastian Struski": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Simon Cowie": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Sneha Saileshkumar": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Socrates Tiaga": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Sorin Ratiu": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Stanislaw Dunat": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Stephen Smith": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Stephen Watts": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Timothy Hebborn": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Tomasz Gierlach": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Vitalijs Kondrasovs": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
            "Zachary Johnson": {
                "superleague": 0,
                "division_1": 0,
                "division_2": 0,
                "division_3": 0,
            },
        }

        h = HtmlGameParser()
        for g in self.games:
            division = h.find_division(g.division)
            if g.r1 in subset:
                subset[g.r1][division] += 1
            if g.r2 in subset:
                subset[g.r2][division] += 1

        for name, count in subset.items():
            print(
                f"{name},{count['superleague']},{count['division_1']},{count['division_2']},{count['division_3']}"
            )

        # TODO: complete this
        return

    # TODO: plot total referees per division (pie chart?)

    def generate_community_graph(self):
        # Extract edges between Home and Away teams
        edges = list(zip(self.dataframe["Home"], self.dataframe["Away"]))

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
        g.vs["community"] = communities.membership

        # Plot the graph with communities
        layout = g.layout("fr", niter=5000)
        ig.plot(
            communities,
            layout=layout,
            palette=palette,
            vertex_label=g.vs["name"],
            vertex_label_size=6,
            vertex_size=5,
            vertex_color=[f"#{c:06x}" for c in g.vs["community"]],
            bbox=(1920, 1080),  # Increase the size of the plot
            margin=50,  # Add margin to reduce clutter at the edges
            target="/tmp/communities_teams.pdf",
        )

    def generate_connected_components_graph(self):
        # Extract edges between Home and Away teams
        good_edges = []
        edges = list(zip(self.dataframe["R1"], self.dataframe["R2"]))
        print(len(edges))

        bad = ["TBC", 119979, 116921, 119791, "119979", "116921", "119791"]
        good = [
            "Ignacio Diez",
            "Jayne Jones",
            "Richard Burbedge",
            "Neil Bentley",
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

    def plot_referee_team_diversity(self):
        """Show the number of different temas each ref has refereed"""
        teams = {}
        for g in self.games:
            if g.r1 not in teams:
                teams[g.r1] = set()
            if g.r2 not in teams:
                teams[g.r2] = set()
            teams[g.r1].add(g.home)
            teams[g.r1].add(g.away)
            teams[g.r2].add(g.home)
            teams[g.r2].add(g.away)

        referees = []
        values = []
        for r in teams:
            if not r:
                continue
            referees.append(r)
            values.append(len(teams[r]))

        df = pandas.DataFrame(dict(referees=referees, count=values))
        fig = px.bar(
            df,
            x=referees,
            y=values,
            color=values,
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        fig.update_layout(
            title_text="Number of Teams per Referee",
            xaxis={"title": "Referees", "categoryorder": "total descending"},
            yaxis={"title": "Number of Teams"},
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def plot_referee_team_diversity_index(self):
        """
        Calculate a 'diversity index' for each referee.
        This is the number of different teams a ref has refereed divided by
        the number of total games that ref has officiated
        """
        teams = {}
        total_games = Counter()
        for g in self.games:
            if g.r1 not in teams:
                teams[g.r1] = set()
            if g.r2 not in teams:
                teams[g.r2] = set()
            teams[g.r1].add(g.home)
            teams[g.r1].add(g.away)
            teams[g.r2].add(g.home)
            teams[g.r2].add(g.away)
            total_games[g.r1] += 1
            total_games[g.r2] += 1

        referees = []
        indices = []
        for r in teams:
            if not r:
                continue
            referees.append(r)
            indices.append(len(teams[r]) / total_games[r])

        df = pandas.DataFrame(dict(referees=referees, indices=indices))
        fig = px.bar(
            df,
            x=referees,
            y=indices,
            color=indices,
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        fig.update_layout(
            title_text="Team Diversity Index",
            xaxis={"title": "Referees", "categoryorder": "total descending"},
            yaxis={"title": "Diversity Index"},
        )
        if self.publish:
            fig.write_html(f"web/charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()
