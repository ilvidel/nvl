import logging
import sys
from datetime import datetime

DIVISIONS = {
    "195838": "Super League Women",
    "196047": "Super League Men",
    "196048": "Division 1 Men",
    "196049": "Division 1 Women",
    "196050": "Division 2 South Men",
    "196051": "Division 2 North Men",
    "196052": "Division 2 Central Men",
    "196053": "Division 2 North Women",
    "196054": "Division 2 West Women",
    "196055": "Division 2 East Women",
    "196056": "Division 3 North Central Men",
    "196057": "Division 3 South East Men",
    "196058": "Division 3 South West Men",
    "196059": "Division 3 North West Men",
    "196061": "Division 3 Central Women",
    "196062": "Division 3 North Women",
    "196063": "Division 3 South East Women",
    "196064": "Division 3 South West Women",
    # "196511": "National Cup Men",
    # "196552": "National Cup Women",
    # "196557": "National Shield Men",
    # "196560": "National Shield Women",
}



class Game(object):
    def __init__(self, attrs={}):
        self.home = attrs['home'] if 'home' in attrs else ""
        self.away = attrs['away'] if 'away' in attrs else ""
        self.timestamp = datetime.fromtimestamp(attrs['timestamp']) if 'timestamp' in attrs else datetime.now()
        self.r1 = attrs['r1'] if 'r1' in attrs else ""
        self.r2 = attrs['r2'] if 'r2' in attrs else ""
        self.venue = attrs['venue'] if 'venue' in attrs else ""
        self.number = attrs['number'] if 'number' in attrs else ""
        self.division = attrs['division'] if 'division' in attrs else ""
        self.category = "women" if "women" in self.division else "men" # this may cause problems with unknwon categories
        self.home_sets = attrs['home_sets'] if 'home_sets' in attrs else 0
        self.away_sets = attrs['away_sets'] if 'away_sets' in attrs else 0

        self.home_points = attrs['home_points'] if 'home_points' in attrs else ["-"] * 5
        self.away_points = attrs['away_points'] if 'away_points' in attrs else ["-"] * 5
        # fill to 5 sets with dashes
        self.home_points.extend("-" * (5-len(self.home_points)))
        self.away_points.extend("-" * (5-len(self.away_points)))

        self.logger = logging.getLogger('nvl')

    def __str__(self):
        return " | ".join(
            [
                self.date(),
                self.time(),
                f"{self.number:8}",
                f"{self.home} vs {self.away}",
                self.division,
                self.venue,
                self.r1,
                self.r2,
            ]
        )

    def __hash__(self):
        return hash(self.division+self.home+self.away+self.date())

    def __eq__(self, other):
        if other.__class__ is not Game:
            return False

        return (
            self.division == other.division
            and self.date() == other.date()
            and self.home == other.home
            and self.away == other.away
            # and self.r1 == other.r1
            # and self.r2 == other.r2
        )

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __add__(self, other):
        """
        Merge self and 'other'
        """
        if self.timestamp != other.timestamp:
            self.logger.error(f"Timestamps differ!: {self.timestamp} / {other.timestamp}")
        if self.division != other.division:
            self.logger.error(f"Divisions differ!: {self.division} / {other.division}")
        if self.number != other.number:
            self.logger.error(f"Game Numbers differ!: {self.number} / {other.number}")
        if self.home != other.home:
            self.logger.error(f"Home Teams differ!: {self.home} / {other.home}")
        if self.away != other.away:
            self.logger.error(f"Away Teams differ!: {self.away} / {other.away}")
        if self.r1 != other.r1:
            self.logger.error(f"R1 differ!: {self.r1} / {other.r1}")
        if self.r2 != other.r2:
            self.logger.error(f"R2 differ!: {self.r2} / {other.r2}")
        if self.venue != other.venue:
            self.logger.error(f"Venues differ!: {self.venue} / {other.venue}")

        game = Game()
        game.timestamp = self.pick(self.timestamp, other.timestamp, "time")
        game.number = self.pick(self.number, other.number, "number")
        game.home = self.pick(self.home, other.home, "home")
        game.away = self.pick(self.away, other.away, "away")
        game.home_sets = self.pick(self.home_sets, other.home_sets, "home sets")
        game.home_points = self.pick(self.home_points, other.home_points, "home points")
        game.away_sets = self.pick(self.away_sets, other.away_sets, "away sets")
        game.away_points = self.pick(self.away_points, other.away_points, "away points")
        game.venue = self.pick(self.venue, other.venue, "venue")
        game.r1 = self.pick(self.r1, other.r1, "R1")
        game.r2 = self.pick(self.r2, other.r2, "R2")
        game.category = self.pick(self.category, other.category, "category")
        game.division = self.pick(self.division, other.division, "division")

        print(f"\nAdding:\n{self.csv()}\n{other.csv()}")
        print(f"Result:\n{game.csv()}")
        # answer = input("Continue? [y/n]:")
        # if answer != "y":
        #     sys.exit(-1)
        return game

        # self.home_sets = other.home_sets
        # self.home_points = other.home_points
        # self.away_sets = other.away_sets
        # self.away_points = other.away_points
        # if other.r1:
        #     self.r1 = other.r1
        # if other.r2:
        #     self.r2 = other.r2
        # if other.venue:
        #     self.venue = other.venue
        # if self.timestamp != other.timestamp:
        #     self.logger.warning(f"[{self.number}] Modifying date from {self.date()} {self.time()} to {other.date()} {other.time()}")
        #     self.timestamp = other.timestamp
        # return self

    def pick(self, a, b, name):
        if not a and b:
            return b
        if not b and a:
            return a
        if not a and not b:
            self.logger.debug(f"Both values for {name} ({a}, {b}) are undefined")
            return ""
        return b

    def to_dict(self):
        return {
            "home": self.home,
            "away": self.away,
            "timestamp": self.timestamp.timestamp(),
            "date": self.date(),
            "time": self.time(),
            "r1": self.r1,
            "r2": self.r2,
            "venue": self.venue,
            "number": self.number,
            "division": self.division,
            "category": self.category,
            "home_sets": self.home_sets,
            "away_sets": self.away_sets,
            "home_points": self.home_points,
            "away_points": self.away_points,
        }

    def csv(self):
        try:
            text =  ",".join(
            [
                self.date(),
                self.time(),
                self.number,
                self.home,
                str(self.home_sets),
                " ".join(self.home_points),
                self.away,
                str(self.away_sets),
                " ".join(self.away_points),
                self.division,
                self.category,
                self.venue,
                self.r1,
                self.r2,
            ]
        )
        except TypeError as e:
            self.logger.error(e)
            self.logger.error(self.to_dict())
        return text

    @staticmethod
    def from_csv(line):
        g = Game()
        g.set_timestamp(f"{line['Date']}T{line['Time']}", numerical=True)
        g.number=line['ID']
        g.home=line['Home']
        g.home_sets=line['HSets']
        g.home_points = line['HPoints'].split()
        g.away=line['Away']
        g.away_sets=line['ASets']
        g.away_points = line['APoints'].split()
        g.venue=line['Venue']
        g.category=line['Category']
        g.division=line['Division']
        g.r1=line['R1']
        g.r2=line['R2']
        return g

    def set_timestamp(self, date_str, numerical=False):
        date_str = date_str.replace("th", "")
        date_str = date_str.replace("1st", "1")
        date_str = date_str.replace("2nd", "2")
        date_str = date_str.replace("3rd", "3")
        if numerical:
            fmt = "%Y-%m-%dT%H:%M"
        else:
            fmt = "%a %d %B %YT%H:%M"
        self.timestamp = datetime.strptime(date_str, fmt)

    def date(self):
        return self.timestamp.date().isoformat()

    def time(self):
        return self.timestamp.time().strftime("%H:%M")

    def set_results(self, results):
        if not results:
            return
        self.home_sets = results[0]
        self.away_sets = results[1]

        self.home_points = results[2::2]
        self.away_points = results[3::2]

        # fill to 5 sets with dashes
        self.home_points.extend("-" * (5-len(self.home_points)))
        self.away_points.extend("-" * (5-len(self.away_points)))

    def as_table_row(self):
        return (
            f"<tr><div>\n"
            f"<td rowspan='2'>{self.date()}</td>\n"
            f"<td rowspan='2'>{self.time()}</td>\n"
            f"<td rowspan='2'>{self.number}</td>\n"
            f"<td rowspan='2'>{self.division}</td>\n"
            f"<td>{self.home}</td>\n"
            f"<td class='sets'>{self.home_sets}</td>\n"
            f"<td>{'</td><td>'.join(self.home_points)}</td>\n"
            f"<td rowspan='2'>{self.venue}</td>\n"
            f"<td rowspan='2'>{self.r1}</td>\n"
            f"<td rowspan='2'>{self.r2}</td>\n"
            "</tr>\n<tr>"
            f"<td>{self.away}</td>\n"
            f"<td class='sets'>{self.away_sets}</td>\n"
            f"<td>{'</td><td>'.join(self.away_points)}</td>\n"
            "</div></tr>\n"
        )
