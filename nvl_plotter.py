import csv

import pandas

from game import Game


class NvlPlotter:
    def __init__(self, filename: str, write_files=False):
        self.games = []
        self.publish = write_files
        with open(filename, "r") as csv_file:
            csv_games = csv.DictReader(csv_file)
            for g in csv_games:
                self.games.append(Game.from_csv(g))

        self.dataframe = pandas.read_csv(filename)

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
