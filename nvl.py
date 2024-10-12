#!/usr/bin/env python3
import json
import re

import bs4

import generator
from game import Game, DIVISIONS


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
    with open(fname, "r") as f:
        text = f.read()
    return text

def load_json(fname):
    with open(fname, "r") as f:
        content = json.load(f)
    print(f"Loaded {len(content)} games from {fname}")
    return [Game(g) for g in content]


# def write_csv(games):
#     with open("nvl.csv", "w") as f:
#         header = "Date,Time,ID,Home,Away,Category,Division,Venue,Ref1, Ref2\n"
#         f.write(header)
#         for g in games:
#             f.write(f"{g.csv()}\n")
#


def write_json(matches, filename):
    print(f"Writing {filename}")
    with open(filename, "w") as f:
        f.write(json.dumps([m.to_dict() for m in matches], indent=2))


def parse_games(games, div):
    game_list = []
    for entry in games:
        game = Game()
        game.home = entry.attrs['data-home-team']
        game.away = entry.attrs['data-away-team']
        date = entry.attrs['data-date']
        game.division = div

        # parse the insides of the game
        soup = bs4.BeautifulSoup(entry.renderContents(), features="html5lib")
        spans = soup.findAll("span")
        lis = soup.findAll("li")

        for tag in lis:
            if tag.find('br'):
                time = tag.contents[0].strip()
                game.set_timestamp(f"{date}T{time}")
                game.number = tag.contents[2].strip().replace(" - Super League Live", "").strip()

        for tag in spans:
            if 'Venue' in tag.text:
                txt = tag.text[len('venue:'):].replace(",", "").replace("\n", "")
                game.venue = re.sub("  +", "-", txt).strip()

            if 'Referee 1' in tag.text:
                game.r1 = tag.text.split(':')[1].strip()

            if 'Referee 2' in tag.text:
                game.r2 = tag.text.split(':')[1].strip()

        game_list.append(game)
    return game_list


def parse_results(games, div):
    game_list = []
    for entry in games:
        game = Game()
        game.home = entry.attrs['data-home-team']
        game.away = entry.attrs['data-away-team']
        date = entry.attrs['data-date']
        game.set_timestamp(f"{date}T00:00")
        game.division = div

        # parse the insides of the game
        soup = bs4.BeautifulSoup(entry.renderContents(), features="html5lib")
        spans = soup.findAll("span")

        results = []
        for tag in spans:
            if tag.attrs:  # skip tags with attributes
                continue
            if tag.text.isnumeric():
                results.append(int(tag.text))
            if "Referee 1" in tag.text:
                game.r1 = tag.text.split(":")[1].strip()
            if "Referee 2" in tag.text:
                game.r2 = tag.text.split(":")[1].strip()
            if "Venue" in tag.text:
                game.venue = tag.text.split(":")[1].strip()
        game.set_results(results)
        game_list.append(game)
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
            print(f"Warning: Game {res} not found in database, adding")
            missing.append(res)
            continue
        index = database.index(res)
        print(f"Adding results for: {res}")
        # database[index] += res
        database[index].home_sets = res.home_sets
        database[index].home_points = res.home_points
        database[index].away_sets = res.away_sets
        database[index].away_points = res.away_points

        if not database[index].r1:
            database[index].r1 = res.r1
        if not database[index].r2:
            database[index].r2 = res.r2
        if not database[index].venue:
            database[index].venue = res.venue

    database.extend(missing)
    # with open("missing.json", "w") as f:
    #     f.write(json.dumps([g.to_dict() for g in missing], indent=2))
    return database



if __name__ == "__main__":
    unplayed_games = []
    played_games = []
    for cid, division in DIVISIONS.items():
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
    write_json(unplayed_games, "unplayed.json")
    write_json(played_games, "results.json")

    unplayed_games = load_json("unplayed.json")
    played_games = load_json("results.json")

    # merge the games
    games = load_json("nvl.json")  # this will be my database
    games = merge_results(games, played_games)
    # look_for_updates(games, unplayed_games)

    # generate the final page
    generator.generate_html(games)
