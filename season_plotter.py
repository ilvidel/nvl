from collections import Counter

import pandas
from plotly import express as px
import igraph as ig
from history_plotter import HistoryPlotter
import matplotlib.pyplot as plt


class SeasonPlotter(HistoryPlotter):
    """Generate charts for a particular season"""

    def __init__(self, filename):
        super().__init__(filename)

    def plot_total_games_per_referee(self):
        """Bar chart of the total number of games per referee"""
        from collections import Counter

        refs = []
        for g in self.games:
            if g.r2 and not g.r2.isnumeric() and not g.r2 == "TBC":
                refs.append(g.r2)
            if g.r1 and not g.r1.isnumeric() and not g.r1 == "TBC":
                refs.append(g.r1)

        c = Counter(refs)

        df = pandas.DataFrame(dict(refs=c.keys(), count=c.values()))

        fig = px.bar(
            df,
            y="count",
            x="refs",
            title="Games per referee",
            color="count",
            color_continuous_scale="rdbu",
        )
        fig.update_layout(
            xaxis={"categoryorder": "total descending", "title": "Referee"},
            yaxis={"title": "Number of Games"},
        )

        fig.show()

    # todo: plot total referees per division (pie chart?)

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
        fig.show()
