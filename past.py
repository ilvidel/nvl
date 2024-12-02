#!/usr/bin/env python3
import json
import os
import re
import sys

import bs4

import generator
from game import Game, DIVISIONS
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[{levelname:^8.8}] {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger('nvl')


def load_file(fname):
    logger.debug(f"Reading from {fname}")
    with open(fname, "r") as f:
        text = f.read()
    return text

def load_json(fname):
    logger.debug(f"Reading from {fname}")
    with open(fname, "r") as f:
        content = json.load(f)
    print(f"Loaded {len(content)} games from {fname}")
    return [Game(g) for g in content]

def write_csv(games):
    with open("past.csv", "w") as f:
        header = "date,time,ID,home,home_sets,home_points,away,away_sets,away_points,division,category,venue,r1,r2\n"
        f.write(header)
        for g in games:
            f.write(f"{g.csv()}\n")

def write_json(matches, filename):
    with open(filename, "w") as f:
        f.write(json.dumps([m.to_dict() for m in matches], indent=2))
    logger.info(f"Wrote {len(matches)} games to {filename}")

def parse_results(games, div, cat):
    logger.info(f"Parsing {len(games)} results in {div} {cat}...")
    game_list = []
    for entry in games:
        game = Game()
        game.home = entry.attrs['data-home-team']
        game.away = entry.attrs['data-away-team']
        date = entry.attrs['data-date']
        game.set_timestamp(f"{date}T00:00")
        game.division = div
        game.category = cat
        logger.debug(f"Found home team: {game.home}")
        logger.debug(f"Found away team: {game.away}")
        logger.debug(f"Found game date: {date}")

        # parse the insides of the game
        soup = bs4.BeautifulSoup(entry.renderContents(), features="html.parser")
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
                game.venue = tag.text.split(":")[1].strip()
                logger.debug(f"Found game venue: {game.venue}")
        game.set_results(results)
        logger.debug(f"Found game results: {results}")

        game_list.append(game)
        logger.info(f"Parsed results for: {game}")
    return game_list

if __name__ == "__main__":
    games = []
    seasons = set()
    categories = set()
    divisions = [
        'challenge_series',
        'cup',
        'division_1',
        'division_2',
        'division_3',
        'playoffs',
        'shield',
        'superleague',
    ]

    # get the files for the past
    filelist = os.listdir()
    past_files = list(filter(lambda f: f.startswith("past"), filelist))

    regex = "past-([\\d\\-]+)-([a-z]+)_([\\w]+)\\.html"
    for filename in sorted(past_files):
        logger.info(f"Processing {filename}...")
        matches = re.match(regex, filename)
        if not matches:
            logger.error(f"No match for {filename}")
            continue
        groups = matches.groups()
        season = groups[0]
        category = groups[1]
        division = "unknown"
        for d in divisions:
            if d in groups[2]:
                division = d

        if division == "unknown":
            logger.error(f"  CAT: {category} DIV: {division} YEAR: {season}")
        else:
            logger.info(f"  CAT: {category} DIV: {division} YEAR: {season}")

        # parse the played games to get results
        html = load_file(filename)
        soup = bs4.BeautifulSoup(html, features="html.parser")
        raw_games = soup.findAll('div', attrs={'class': "col-12 mb-4 resultContents"})
        games.extend(parse_results(raw_games, division, category))

    # save games to file
    write_csv(games)