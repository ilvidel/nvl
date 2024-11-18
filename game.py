import logging
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
            and self.r1 == other.r1
            and self.r2 == other.r2
        )

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __add__(self, other):
        """
        NON-COMMUTATIVE: Gets the results of 'other' into 'self'
        """
        self.home_sets = other.home_sets
        self.home_points = other.home_points
        self.away_sets = other.away_sets
        self.away_points = other.away_points
        if other.r1:
            self.r1 = other.r1
        if other.r2:
            self.r2 = other.r2
        if other.venue:
            self.venue = other.venue
        if self.timestamp != other.timestamp:
            self.logger.warning(f"Modifying date from {self.date()} {self.time()} to {other.date()} {other.time()}")
            self.timestamp = other.timestamp
        return self

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
            "home_sets": self.home_sets,
            "away_sets": self.away_sets,
            "home_points": self.home_points,
            "away_points": self.away_points,
        }

    def csv(self):
        return ",".join(
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
                self.venue,
                self.r1,
                self.r2,
            ]
        )

    def set_timestamp(self, date_str):
        date_str = date_str.replace("th", "")
        date_str = date_str.replace("st", "")
        date_str = date_str.replace("nd", "")
        date_str = date_str.replace("rd", "")
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
