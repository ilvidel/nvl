#!/usr/bin/env python3
import csv
import datetime
import json
import re

import bs4

import generator
from game import Game, DIVISIONS
import logging

logging.basicConfig(
    level=logging.WARNING,
    format="[{levelname:^8.8}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger('nvl')


# def save_page(category_id):
#     url = "https://competitions.volleyzone.co.uk/fixture-and-results/nvl/"
#     response = requests.get(url)
#
#     if not response.ok:
#         print(response.reason)
#         print(response.json())
#         sys.exit(1)
#
#     with open(FILENAME, "w") as f:
#         f.writelines(response.text)

def load_file(fname):
    logger.debug(f"Reading from {fname}")
    with open(fname, "r") as f:
        text = f.read()
    return text

# def load_json(fname):
#     logger.debug(f"Reading from {fname}")
#     with open(fname, "r") as f:
#         content = json.load(f)
#     print(f"Loaded {len(content)} games from {fname}")
#     return [Game(g) for g in content]

# def write_json(matches, filename):
#     with open(filename, "w") as f:
#         f.write(json.dumps([m.to_dict() for m in matches], indent=2))
#     logger.info(f"Wrote {len(matches)} games to {filename}")

def load_csv(filename):
    games = []
    with open(filename, "r") as csv_file:
        csv_games = csv.DictReader(csv_file)
        for g in csv_games:
            games.append(Game.from_csv(g))
    return games

def write_csv(games, filename):
    with open(filename, "w") as f:
        header = "Date,Time,ID,Home,HSets,HPoints,Away,ASets,APoints,Division,Category,Venue,R1,R2,\n"
        f.write(header)
        for g in games:
            f.write(f"{g.csv()}\n")


def parse_games(games, div):
    logger.info(f"Parsing {len(games)} games in {div}...")
    game_list = []
    for entry in games:
        game = Game()
        game.home = entry.attrs['data-home-team']
        game.away = entry.attrs['data-away-team']
        date = entry.attrs['data-date']
        game.division = div
        game.set_category()
        logger.debug(f"Found home team: {game.home}")
        logger.debug(f"Found away team: {game.away}")
        logger.debug(f"Found game date: {game.date()}")

        # parse the insides of the game
        soup = bs4.BeautifulSoup(entry.renderContents(), features="html5lib")
        spans = soup.findAll("span")
        lis = soup.findAll("li")

        for tag in lis:
            if tag.find('br'):
                time = tag.contents[0].strip()
                logger.debug(f"Found game time: {time}")
                game.set_timestamp(f"{date}T{time}")
                try:
                    game.number = tag.contents[2].strip().replace(" - Super League Live", "").strip()
                    logger.debug(f"Found game number: {game.number}")
                except IndexError:
                    game.number = ""

        for tag in spans:
            if 'Venue' in tag.text:
                txt = tag.text[len('venue:'):].replace(",", "").replace("\n", "")
                game.venue = re.sub("  +", "-", txt).strip()
                logger.debug(f"Found game venue: {game.venue}")

            if 'Referee 1' in tag.text:
                game.r1 = tag.text.split(':')[1].replace("(Pending)", "").strip()
                logger.debug(f"Found game R1: {game.r1}")

            if 'Referee 2' in tag.text:
                game.r2 = tag.text.split(':')[1].replace("(Pending)", "").strip()
                logger.debug(f"Found game R2: {game.r2}")

        logger.info(f"Adding game: {game}")
        game_list.append(game)
    return game_list


def parse_results(games, div):
    logger.info(f"Parsing {len(games)} results in {div}...")
    game_list = []
    for entry in games:
        game = Game()
        game.home = entry.attrs['data-home-team']
        game.away = entry.attrs['data-away-team']
        date = entry.attrs['data-date']
        game.set_timestamp(f"{date}T00:00")
        game.division = div
        game.set_category()
        logger.debug(f"Found home team: {game.home}")
        logger.debug(f"Found away team: {game.away}")
        logger.debug(f"Found game date: {date}")

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
                game.r1 = tag.text.split(":")[1].replace("(Pending)", "").strip()
                logger.debug(f"Found game R1: {game.r1}")
            if "Referee 2" in tag.text:
                game.r2 = tag.text.split(":")[1].replace("(Pending)", "").strip()
                logger.debug(f"Found game R2: {game.r2}")
            if "Venue" in tag.text:
                game.venue = tag.text.split(":")[1].strip().replace(",", "")
                logger.debug(f"Found game venue: {game.venue}")
        game.set_results(results)
        logger.debug(f"Found game results: {results}")

        game_list.append(game)
        logger.info(f"Parsed results for: {game}")
    return game_list


def merge_results(database, results):
    """
    Add the results from 'results' into the corresponding game in 'database'.
    All games in 'results' should have a corresponding game in 'database';
     otherwise there must have been some update to the details (referees, time, date, etc...)
    """
    missing = []
    for res in results:
        if res not in database:
            logger.warning(f"Game {res} not found in database. Adding")
            missing.append(res)
            continue
        index = database.index(res)
        logger.info(f"Adding results for: {res}")
        database[index] += res
        # database[index].home_sets = res.home_sets
        # database[index].home_points = res.home_points
        # database[index].away_sets = res.away_sets
        # database[index].away_points = res.away_points
        #
        # if not database[index].r1:
        #     database[index].r1 = res.r1
        # if not database[index].r2:
        #     database[index].r2 = res.r2
        # if not database[index].venue:
        #     database[index].venue = res.venue

    database.extend(missing)
    # with open("missing.json", "w") as f:
    #     f.write(json.dumps([g.to_dict() for g in missing], indent=2))
    return database


def look_for_updates(database, unplayed):
    for g in unplayed:
        index = -1
        if g.number:
            filtro = list(filter(lambda x: x.number == g.number, database))
        else:
            filtro = list(filter(lambda x: x.home == g.home and x.away==g.away and x.division==g.division, database))

        try:
            index = database.index(filtro[0])
        except IndexError as ie:
            logger.error(f"No game matching number '{g.number}': {g}")
            database.append(g)
        except ValueError as ve:
            logger.error(f"Game not found in database: {g}")
            database.append(g)

        if database[index] != g:
            logger.warning(f"Unmatched game {g.number}, merging")
            logger.debug(g)
            logger.debug(database[index])
            database[index] += g


if __name__ == "__main__":
    start = datetime.datetime.now()
    unplayed_games = []
    played_games = []
    for _, division in DIVISIONS.items():
        # parse the unplayed games
        filename = division.replace(" ", "_").lower() + ".html"
        html = load_file(filename)
        soup = bs4.BeautifulSoup(html, features="html5lib")
        raw_games = soup.findAll('div', attrs={'class': "col-12 mb-4 FixContents"})
        unplayed_games.extend(parse_games(raw_games, division))

        # parse the played games to get results
        filename = "results-" + filename
        html = load_file(filename)
        soup = bs4.BeautifulSoup(html, features="html5lib")
        raw_games = soup.findAll('div', attrs={'class': "col-12 mb-4 resultContents"})
        played_games.extend(parse_results(raw_games, division))

    # save games to file
    # write_json(unplayed_games, "unplayed.json")
    # write_json(played_games, "results.json")
    write_csv(unplayed_games, "unplayed.csv")
    write_csv(played_games, "results.csv")

    # merge the games
    # games = load_json("nvl.json")  # this will be my database
    games = load_csv("nvl.csv")  # this will be my database
    games = merge_results(games, played_games)
    look_for_updates(games, unplayed_games)

    # generate the final page
    generator.generate_html(games)
    # write_json(sorted(set(games)), "nvl.json")
    write_csv(sorted(games, key=lambda x: x.timestamp), "nvl.csv")

    end = datetime.datetime.now()
    print(f"{(end - start).total_seconds()} seconds")
