from interactive_plotter import InteractivePlotter
from history_plotter import HistoryPlotter
from season_plotter import SeasonPlotter

if __name__ == "__main__":
    history = HistoryPlotter('past.csv')
    season = SeasonPlotter('nvl.csv')
    actionable = InteractivePlotter('nvl.csv')

    history.plot_total_points_by_category()
    history.plot_total_points_per_number_of_sets()
    history.plot_frequency_of_results()
    history.plot_home_victories()
    history.plot_home_victories_per_division()
    history.plot_number_of_games_per_season()
    history.plot_number_of_games_per_season_by_division()
    history.plot_number_of_teams_per_season_by_division()
    history.plot_number_of_teams_per_season()

    history.plot_referees_per_year()  # fixme: github issue #5

    season.plot_total_games_per_referee()
    season.plot_referee_team_diversity()
    season.plot_referee_team_diversity_index()

    # REFEREES - Individual charts
    for r in history.referee_subset:  # TODO: change to the full set of referees
        actionable.referee_plot_role_count(r)  # fixme: github issue #6
        actionable.referee_plot_division_count(r)  # fixme: github issue #6
        actionable.referee_plot_category_count(r)  # fixme: github issue #6
        actionable.referee_plot_team_count(r)  # fixme: github issue #6

    actionable.referee_plot_venue_count()
    actionable.referee_plot_game_count_over_time()
    actionable.referee_plot_pairings_piechart()

    # plotter.generate_community_graph() # fixme: not working yet
    # plotter.generate_connected_components_graph() # fixme: not working yet

    # plotter.plot_referee_network(directed=False)
    # plotter.plot_teams_network()

    # TEAMS
    teams = set()
    for g in history.games:
        teams.add(g.away)
        teams.add(g.home)
    for t in teams:
        if 'Bristol' in t:
            actionable.team_plot_referee_count(t)  # fixme: github issue #6
