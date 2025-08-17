import inspect
from collections import Counter

import pandas
import plotly.graph_objects as go
from nvl_plotter import NvlPlotter
from plotly import express as px


class InteractivePlotter(NvlPlotter):
    """Generate interactive charts, where you can choose from a dropdown"""
    def referee_plot_game_count_over_time(self):
        """
        Interactive bar chart, showing the number of games
        that a particular referee has officiated each season
        """
        # Extract relevant data from Game objects
        game_data = [
            (game.timestamp.year, game.division, game.r1, game.r2)
            for game in self.games
        ]
        df = pandas.DataFrame(game_data, columns=["Year", "Division", "R1", "R2"])
        # df['Year'] = pandas.to_datetime(df['Date']).dt.year

        referees = set(df["R1"]).union(set(df["R2"]))

        dropdown_buttons = []
        fig = go.Figure()

        for referee in sorted(referees):
            ref_games = df[(df["R1"] == referee) | (df["R2"] == referee)]
            grouped_data = (
                ref_games.groupby(["Year", "Division"]).size().unstack(fill_value=0)
            )

            traces = []
            for division in grouped_data.columns:
                traces.append(
                    go.Bar(
                        x=grouped_data.index,
                        y=grouped_data[division],
                        name=division,
                        visible=False,
                    )
                )

            dropdown_buttons.append(
                {
                    "label": referee,
                    "method": "update",
                    "args": [
                        {
                            "visible": [
                                (
                                    True
                                    if i // len(grouped_data.columns)
                                    == list(referees).index(referee)
                                    else False
                                )
                                for i in range(
                                    len(referees) * len(grouped_data.columns)
                                )
                            ]
                        },
                        {"title.text": f"Games Officiated by {referee} Per Year"},
                    ],
                }
            )

            fig.add_traces(traces)

        fig.update_layout(
            title=f"Games Officiated by {list(referees)[0]} Per Year",
            xaxis_title="Year",
            yaxis_title="Number of Games",
            barmode="stack",
            updatemenus=[
                {"buttons": dropdown_buttons, "direction": "down", "showactive": True}
            ],
        )

        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_role_count(self, ref_name):
        """Plot the number of R1 vs R2 roles for a particular referee"""
        r1 = len(list(filter(lambda g: g.r1 == ref_name, self.games)))
        r2 = len(list(filter(lambda g: g.r2 == ref_name, self.games)))
        both = len(
            list(filter(lambda g: g.r1 == ref_name and g.r2 == ref_name, self.games))
        )

        donut_colors = ["#26547C", "#EF476F", "#FFD166", "#06D6A0"]
        labels = ["Ref1", "Ref2", "Both"]
        values = [r1, r2, both]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    direction="clockwise",
                    sort=False,  # do not sort by value
                    hole=0.5,
                    title=f"Roles for {ref_name}",
                )
            ]
        )
        fig.update_traces(
            textinfo="label+percent+value", marker=dict(colors=donut_colors)
        )
        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_division_count(self, ref_name):
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
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    sort=False,  # do not sort by value
                    hole=0.5,
                    title=f"Number of Games {ref_name}",
                )
            ]
        )
        fig.update_traces(
            textinfo="label+percent+value", marker=dict(colors=donut_colors)
        )
        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_category_count(self, ref_name):
        """Plot the number of games by a particular referee, per category"""
        games = list(filter(lambda g: g.r1 == ref_name or g.r2 == ref_name, self.games))
        men = len(list(filter(lambda g: "men" == g.category, games)))
        ladies = len(list(filter(lambda g: "women" == g.category, games)))

        donut_colors = ["#26547C", "#EF476F", "#FF66", "#06D6A0"]
        labels = ["Men", "Ladies"]
        values = [men, ladies]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    sort=False,  # do not sort by value
                    hole=0.5,
                    title=f"Number of Games by {ref_name}",
                )
            ]
        )
        fig.update_traces(
            textinfo="label+percent+value", marker=dict(colors=donut_colors)
        )
        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_team_count(self, ref_name):
        """Plot the number of times a referee has officiated each team"""
        games = list(filter(lambda g: g.r1 == ref_name or g.r2 == ref_name, self.games))
        teams = []
        for g in games:
            teams.append(f"{g.home} ({g.division})")
            teams.append(f"{g.away} ({g.division})")

        print(f"Total teams: {len(teams)}")
        import collections

        c = collections.Counter(teams)
        df = pandas.DataFrame(dict(teams=c.keys(), count=c.values()))
        fig = px.bar(
            df,
            y="teams",
            x="count",
            color="count",
            title=f"Teams for {ref_name}",
            color_continuous_scale=px.colors.sequential.solar,
            orientation="h",
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending", "title": "Teams"},
            xaxis={"title": "Times refereed"},
        )
        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_venue_count(self):
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
        fig.add_trace(
            go.Pie(
                labels=referees,
                values=venues,
                name=first_ref,
                marker=dict(colors=px.colors.qualitative.Safe),
                hole=0.5,
            )
        )

        # Create dropdown menu
        dropdown_buttons = []
        for ref in sorted(all_referees):
            dropdown_buttons.append(
                {
                    "label": ref,
                    "method": "update",
                    "args": [
                        {
                            "labels": [list(co_occurrence[ref].keys())],
                            "values": [list(co_occurrence[ref].values())],
                        },
                        {"title.text": f"Where has {ref} Officiated?"},
                    ],
                }
            )

        fig.update_traces(textinfo="label+percent+value")
        fig.update_layout(
            # xaxis_title='Refereed at',
            # yaxis_title='Number of games',
            # xaxis={'categoryorder': 'total descending'},
            updatemenus=[
                {"buttons": dropdown_buttons, "direction": "down", "showactive": True}
            ]
        )

        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_pairigs_barchart(self):
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
        fig.add_trace(
            go.Bar(
                x=x_values,
                y=y_values,
                name=first_ref,
                marker=dict(color=y_values, colorscale="viridis"),
            )
        )

        # Create dropdown menu
        dropdown_buttons = []
        for ref in sorted(all_referees):
            dropdown_buttons.append(
                {
                    "label": ref,
                    "method": "update",
                    "args": [
                        {
                            "x": [list(co_occurrence[ref].keys())],
                            "y": [list(co_occurrence[ref].values())],
                            "marker": [
                                dict(
                                    color=list(co_occurrence[ref].values()),
                                    colorscale="viridis",
                                )
                            ],
                        },
                        {"title.text": f"Number of Games Officiated with {ref}"},
                    ],
                }
            )

        fig.update_layout(
            title=f"Number of Games Officiated with {first_ref}",
            xaxis_title="Refereed with",
            yaxis_title="Number of Games",
            xaxis={"categoryorder": "total ascending"},
            updatemenus=[
                {"buttons": dropdown_buttons, "direction": "down", "showactive": True}
            ],
        )

        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def referee_plot_pairings_piechart(self):
        """
        Generates an interactive pie chart showing the number of
        times a referee has officiated with another referee.
        The chart includes a dropdown menu to select a referee.
        """
        # Extract all referees
        referee_pairs = [(game.r1, game.r2) for game in self.games]
        all_referees = set(ref for pair in referee_pairs for ref in pair)
        print("\n".join(sorted(all_referees)))
        print(f"Total referees: {len(all_referees)}")

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
        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                name=first_ref,
                marker=dict(colors=px.colors.qualitative.Safe),
                sort=True,
                hole=0.5,
            )
        )

        # Create dropdown menu
        dropdown_buttons = []
        for ref in sorted(all_referees):
            dropdown_buttons.append(
                {
                    "label": ref,
                    "method": "update",
                    "args": [
                        {
                            "labels": [list(co_occurrence[ref].keys())],
                            "values": [list(co_occurrence[ref].values())],
                        },
                        {"title.text": f"Number of Games Officiated with {ref}"},
                    ],
                }
            )

        fig.update_layout(
            title=f"Number of Referee Pairings for {first_ref}",
            updatemenus=[
                {"buttons": dropdown_buttons, "direction": "down", "showactive": True}
            ],
        )

        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()

    def team_plot_referee_count(self, team_name):
        # TODO: esto es una movida porque por ejemplo,
        #  City of Bristol se llama igual en hombres que en mujeres.
        #  Igual para otros equipos (p.ej. Bristol)
        games = list(
            filter(lambda g: g.home == team_name or g.away == team_name, self.games)
        )
        refs = []
        for g in games:
            refs.append(f"{g.r1} ({g.category})")
            refs.append(f"{g.r2} ({g.category})")

        import collections

        c = collections.Counter(refs)
        df = pandas.DataFrame(dict(refs=c.keys(), count=c.values()))
        fig = px.bar(
            df,
            y="refs",
            x="count",
            color="count",
            title=f"Referees for {team_name}",
            color_continuous_scale=px.colors.sequential.Viridis,
            orientation="h",
        )
        fig.update_layout(
            yaxis={"categoryorder": "total ascending", "title": "Referees"},
            xaxis={"title": "Times refereed"},
        )
        if self.publish:
            fig.write_html(f"charts/{inspect.stack()[0][3]}.html")
        else:
            fig.show()
