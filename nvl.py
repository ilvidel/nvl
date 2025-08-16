#!/usr/bin/env python3
import argparse
import csv
import datetime
import logging

import bs4

from game import Game

logging.basicConfig(
    level=logging.WARNING,
    format="[{levelname:^8.8}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def check_unknown(token):
    bad = ["TBC", "110308", "119979", "116921", "119791", "", None]
    if token in bad:
        return "unknown"
    return token


def are_results_valid(results):
    """
    Validates if a volleyball game result is valid.

    Returns:
        bool: True if the results are valid, False otherwise
    """
    results = [int(n) for n in results]
    # Check if we have at least the number of sets won by each team
    if len(results) < 2:
        return False

    sets_home = results[0]
    sets_away = results[1]

    # Basic validation for set counts
    if sets_home < 0 or sets_away < 0:
        return False

    # Standard volleyball rules: first to 3 sets wins (best of 5)
    if sets_home + sets_away > 5:
        return False

    if sets_home > 3 or sets_away > 3:
        return False

    # At least one team must reach 3 sets to win
    if sets_home != 3 and sets_away != 3:
        return False

    # The points data should be enough to represent all sets
    # Each set needs 2 entries (home score and away score)
    expected_point_entries = (sets_home + sets_away) * 2
    actual_point_entries = len(results) - 2

    # if actual_point_entries != expected_point_entries:
    #     return False

    # Validate points for each set
    for i in range(0, actual_point_entries, 2):
        home_points = results[i + 2]  # +2 to skip the set counts
        away_points = results[i + 3]

        # Points can't be negative
        if home_points < 0 or away_points < 0:
            return False

        # Determine if this is the deciding set (5th set)
        is_deciding_set = (i // 2) + 1 == 5

        # Regular sets require 25 points minimum with 2-point lead
        # Deciding set (5th) requires 15 points minimum with 2-point lead
        min_points = 15 if is_deciding_set else 25

        # Check if the winner has enough points and has a 2-point lead
        if home_points > away_points:
            if home_points < min_points:
                return False
            if home_points - away_points < 2:
                return False
        elif away_points > home_points:
            if away_points < min_points:
                return False
            if away_points - home_points < 2:
                return False
        else:
            # Scores can't be tied in a completed set
            # return False
            # Pass because VE completes unplayed sets with 0-0
            pass

    # # Count sets based on points to verify they match the reported set counts
    # calculated_home_sets = 0
    # calculated_away_sets = 0
    #
    # for i in range(0, actual_point_entries, 2):
    #     home_points = results[i + 2]
    #     away_points = results[i + 3]
    #
    #     if home_points > away_points:
    #         calculated_home_sets += 1
    #     else:
    #         calculated_away_sets += 1
    #
    # # Verify that reported set counts match the calculated ones
    # return sets_home == calculated_home_sets and sets_away == calculated_away_sets
    return True


class HtmlGameParser(object):

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_games(self, raw_games):
        game_list = []
        discarded = 0

        for entry in raw_games:
            game = Game()
            game.home = entry.attrs["data-home-team"]
            game.away = entry.attrs["data-away-team"]
            date = entry.attrs["data-date"]
            game.set_timestamp(f"{date}T00:00")
            game.season = self.calculate_season(game.timestamp)
            self.logger.debug(f"Found home team: {game.home}")
            self.logger.debug(f"Found away team: {game.away}")
            self.logger.debug(f"Found game date: {date}")

            # parse the insides of the game
            soup = bs4.BeautifulSoup(entry.renderContents(), features="html5lib")
            spans = soup.findAll("span")

            results = []
            for tag in spans:
                if tag.attrs:  # skip tags with attributes
                    continue
                if tag.text.isnumeric():
                    results.append(tag.text)
                if "Referee 1" in tag.text:
                    token = tag.text.split(":")[1].replace("(Pending)", "").strip()
                    game.r1 = check_unknown(token)
                    self.logger.debug(f"Found game R1: {game.r1}")
                if "Referee 2" in tag.text:
                    token = tag.text.split(":")[1].replace("(Pending)", "").strip()
                    game.r2 = check_unknown(token)
                    self.logger.debug(f"Found game R2: {game.r2}")
                if "Venue" in tag.text:
                    token = tag.text.split(":")[1].strip().replace(",", "")
                    game.venue = check_unknown(token)
                    self.logger.debug(f"Found game venue: {game.venue}")
                if any(
                    [
                        keyword in tag.text
                        for keyword in [
                            "Division",
                            "Super",
                            "Playoffs",
                            "Cup",
                            "Shield",
                        ]
                    ]
                ):
                    game.category = self.find_category(tag.text)
                    game.division = self.find_division(tag.text)
                    self.logger.debug(
                        f"Found game category: {game.division} {game.category}"
                    )

            game.set_results(results)
            self.logger.debug(f"Found game results: {results}")
            if not are_results_valid(results):
                self.logger.warning(f"Invalid resutls: {game}")
                discarded += 1
                continue

            game_list.append(game)
            self.logger.info(f"Parsed results for: {game}")
        return game_list, discarded

    def parse_files(self, filelist):
        """
        Parse html files from volleyballengland.org to get the results of games.
        Return a list of Game objects
        """
        total_games = []
        invalid = 0
        for filename in filelist:
            self.logger.info(f"Parsing {filename}")
            html = self.load_file(filename)
            soup = bs4.BeautifulSoup(html, features="html5lib")
            raw_games = soup.findAll(
                "div", attrs={"class": "col-12 mb-4 resultContents"}
            )
            parsed_games, discarded = self.parse_games(raw_games)
            invalid += discarded
            total_games.extend(parsed_games)

        total = invalid + len(total_games)
        print(f"Discarded {invalid} out of {total} games ({invalid/total*100}%)")
        return total_games

    def load_file(self, fname):
        self.logger.debug(f"Loading {fname}")
        with open(fname, "r") as f:
            text = f.read()
        return text

    def find_category(self, text):
        if "Women" in text:
            return "women"
        elif "Men" in text:
            return "men"
        else:
            self.logger.error(f"Unknown CATEGORY in {text}")
            return "unknown"

    def find_division(self, text):
        text = text.lower()
        if "cup" in text:
            return "cup"
        elif "shield" in text:
            return "shield"
        elif "super" in text:
            return "superleague"
        elif "division 1" in text:
            return "division_1"
        elif "division 2" in text:
            return "division_2"
        elif "division 3" in text:
            return "division_3"
        elif "playoff" in text:
            return "playoffs"
        else:
            self.logger.error(f"Unknown DIVISION in {text}")
            return "unknown"

    @staticmethod
    def calculate_season(timestamp):
        year = timestamp.year

        # season starts 1st Aug and ends 31st July
        if timestamp.month >= 8:
            return f"{year}-{year + 1}"
        else:
            return f"{year - 1}-{year}"


def load_csv(filename):
    games = []
    with open(filename, "r") as csv_file:
        csv_games = csv.DictReader(csv_file)
        for g in csv_games:
            games.append(Game.from_csv(g))
    return games


def write_csv(games, filename):
    with open(filename, "w") as f:
        header = "season,date,home,home_sets,home_points,away,away_sets,away_points,division,category,venue,r1,r2\n"
        f.write(header)
        for g in games:
            f.write(f"{g.csv()}\n")


# def parse_games(games, div):
#     logger.info(f"Parsing {len(games)} games in {div}...")
#     game_list = []
#     for entry in games:
#         game = Game()
#         game.home = entry.attrs["data-home-team"]
#         game.away = entry.attrs["data-away-team"]
#         date = entry.attrs["data-date"]
#         game.division = div
#         game.set_category()
#         logger.debug(f"Found home team: {game.home}")
#         logger.debug(f"Found away team: {game.away}")
#         logger.debug(f"Found game date: {game.date()}")
#
#         # parse the insides of the game
#         soup = bs4.BeautifulSoup(entry.renderContents(), features="html5lib")
#         spans = soup.findAll("span")
#         lis = soup.findAll("li")
#
#         for tag in lis:
#             if tag.find("br"):
#                 time = tag.contents[0].strip()
#                 logger.debug(f"Found game time: {time}")
#                 game.set_timestamp(f"{date}T{time}")
#                 try:
#                     game.number = (
#                         tag.contents[2]
#                         .strip()
#                         .replace(" - Super League Live", "")
#                         .strip()
#                     )
#                     logger.debug(f"Found game number: {game.number}")
#                 except IndexError:
#                     game.number = ""
#
#         for tag in spans:
#             if "Venue" in tag.text:
#                 txt = tag.text[len("venue:") :].replace(",", "").replace("\n", "")
#                 game.venue = re.sub("  +", "-", txt).strip()
#                 logger.debug(f"Found game venue: {game.venue}")
#
#             if "Referee 1" in tag.text:
#                 game.r1 = tag.text.split(":")[1].replace("(Pending)", "").strip()
#                 logger.debug(f"Found game R1: {game.r1}")
#
#             if "Referee 2" in tag.text:
#                 game.r2 = tag.text.split(":")[1].replace("(Pending)", "").strip()
#                 logger.debug(f"Found game R2: {game.r2}")
#
#         logger.info(f"Adding game: {game}")
#         game_list.append(game)
#     return game_list


# def merge_results(database, results):
#     """
#     Add the results from 'results' into the corresponding game in 'database'.
#     All games in 'results' should have a corresponding game in 'database';
#      otherwise there must have been some update to the details (referees, time, date, etc...)
#     """
#     missing = []
#     for res in results:
#         if res not in database:
#             logger.warning(f"Game {res} not found in database. Adding")
#             missing.append(res)
#             continue
#         index = database.index(res)
#         logger.info(f"Adding results for: {res}")
#         database[index] += res
#         # database[index].home_sets = res.home_sets
#         # database[index].home_points = res.home_points
#         # database[index].away_sets = res.away_sets
#         # database[index].away_points = res.away_points
#         #
#         # if not database[index].r1:
#         #     database[index].r1 = res.r1
#         # if not database[index].r2:
#         #     database[index].r2 = res.r2
#         # if not database[index].venue:
#         #     database[index].venue = res.venue
#
#     database.extend(missing)
#     # with open("missing.json", "w") as f:
#     #     f.write(json.dumps([g.to_dict() for g in missing], indent=2))
#     return database
#
#
# def look_for_updates(database, unplayed):
#     for g in unplayed:
#         index = -1
#         if g.number:
#             filtro = list(filter(lambda x: x.number == g.number, database))
#         else:
#             filtro = list(
#                 filter(
#                     lambda x: x.home == g.home
#                     and x.away == g.away
#                     and x.division == g.division,
#                     database,
#                 )
#             )
#
#         try:
#             index = database.index(filtro[0])
#         except IndexError as ie:
#             logger.error(f"No game matching number '{g.number}': {g}")
#             database.append(g)
#         except ValueError as ve:
#             logger.error(f"Game not found in database: {g}")
#             database.append(g)
#
#         if database[index] != g:
#             logger.warning(f"Unmatched game {g.number}, merging")
#             logger.debug(g)
#             logger.debug(database[index])
#             database[index] += g


if __name__ == "__main__":
    start = datetime.datetime.now()

    unplayed_games = []
    played_games = []

    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Files to parse")
    parser.add_argument("--dest", nargs=1, help="Where to write the parsed games")
    args = parser.parse_args()

    game_parser = HtmlGameParser()
    games = game_parser.parse_files(args.files)

    # save games to file
    # write_csv(sorted(games, key=lambda x: x.timestamp), args.dest[0])
    write_csv(sorted(games), args.dest[0])

    # generate the final page
    # generator.generate_html(games)

    end = datetime.datetime.now()
    print(f"{(end - start).total_seconds()} seconds")
