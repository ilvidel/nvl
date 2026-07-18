"""
Scraper for https://competitions.volleyzone.co.uk/fixture-and-results/

The site's "Fixture and Results" page is a JS widget backed by two
WordPress admin-ajax.php actions:

  1. fetch_season_competitions  (POST seasonID=<id>)
     -> returns every competition/division that exists within that season,
        each with its own competition id (res_compID).

  2. fetch_results_by_competition  (POST res_compID=<id>&seasonID=<season id>)
     -> returns every played result for that division/season, as an HTML
        fragment. This is the same "resultContents" div structure the old
        Selenium-based scraper used to parse from full page source, so we
        reuse the same parsing approach.

No browser / JS execution is required -- these are plain POST requests.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

import bs4
import requests

logger = logging.getLogger("nvl.scraper")

BASE_URL = "https://competitions.volleyzone.co.uk"
AJAX_URL = f"{BASE_URL}/wp-admin/admin-ajax.php"
REFERER = f"{BASE_URL}/fixture-and-results/"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": REFERER,
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE_URL,
}


@dataclass
class Competition:
    id: str
    name: str
    category: str  # "Men" / "Women" (best-effort split of `name`)
    division: str  # remainder of `name` after the category prefix


@dataclass
class Match:
    season: str
    season_id: str
    competition_id: str
    competition_name: str
    category: str
    division: str
    fixture_id: Optional[str]
    home: str
    away: str
    date_str: str
    home_sets: Optional[int] = None
    away_sets: Optional[int] = None
    home_points: list = field(default_factory=list)
    away_points: list = field(default_factory=list)
    venue: str = ""
    r1: str = ""
    r2: str = ""
    extra: dict = field(default_factory=dict)  # any other label:value spans found

    def to_dict(self):
        return {
            "season": self.season,
            "season_id": self.season_id,
            "competition_id": self.competition_id,
            "competition_name": self.competition_name,
            "category": self.category,
            "division": self.division,
            "fixture_id": self.fixture_id,
            "home": self.home,
            "away": self.away,
            "date_str": self.date_str,
            "home_sets": self.home_sets,
            "away_sets": self.away_sets,
            "home_points": self.home_points,
            "away_points": self.away_points,
            "venue": self.venue,
            "r1": self.r1,
            "r2": self.r2,
            "extra": self.extra,
        }


def make_session() -> requests.Session:
    """Create a session, warmed up with a GET to the fixture-and-results page
    so we pick up any cookies the site sets before POSTing to admin-ajax."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    resp = session.get(REFERER, timeout=30)
    resp.raise_for_status()
    return session


def _post(session: requests.Session, action: str, data: dict, retries: int = 3, backoff: float = 2.0):
    url = f"{AJAX_URL}?action={action}"
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.post(url, data=data, timeout=30)
            resp.raise_for_status()
            return resp
        except requests.RequestException as e:
            last_exc = e
            logger.warning(f"Request failed (attempt {attempt}/{retries}) for {action}: {e}")
            time.sleep(backoff * attempt)
    raise last_exc


_CATEGORY_RE = re.compile(r"\b(mens|men's|womens|women's)\b", re.IGNORECASE)


def _split_category_division(name: str) -> tuple[str, str]:
    """
    Handles both naming styles seen across seasons:
      - old style:  "Mens Division 3 North" / "Womens Cup"
      - new style:  "Women's | National Shield" / "Men's | Division 1 North | 26-27"
    """
    match = _CATEGORY_RE.search(name)
    if not match:
        return "", name.strip()

    category = "Women" if match.group(1).lower().startswith("women") else "Men"

    # Remove the matched category token, then clean up leftover separators
    # (pipes, extra whitespace) and drop a trailing "| <season>" suffix
    # (e.g. "| 26-27") if present.
    rest = name[: match.start()] + name[match.end() :]
    parts = [p.strip() for p in rest.split("|")]
    parts = [p for p in parts if p and not re.fullmatch(r"\d{2}-\d{2}", p)]
    division = " ".join(parts).strip(" |").strip()
    return category, division


@dataclass
class Group:
    id: str
    slug: str  # e.g. "nvl", "cups" -- the data-seasonname attribute
    label: str  # display text, e.g. "NVL", "Cups"


# Substrings (data-seasonname) we consider part of "the NVL" for this
# project. Recent seasons bundle many other competition types (juniors,
# beach, sitting, NEVZA, etc.) into the same season, so we filter down to
# groups matching these rather than trying to guess from division names.
# Substring (not exact) match, since slugs vary release to release, e.g.
# "nvl" vs "nvl-draft-fixtures", "cups" vs "national-cup-and-shield".
NVL_GROUP_SUBSTRINGS = ("nvl", "cup", "shield", "challenge")


def _options_to_competitions(html: str) -> list[Competition]:
    soup = bs4.BeautifulSoup(html, features="html.parser")
    competitions = []
    for option in soup.find_all("option"):
        value = option.get("value", "").strip()
        if not value:
            continue  # skip the "All divisions" placeholder
        name = option.text.strip()
        category, division = _split_category_division(name)
        competitions.append(
            Competition(id=value, name=name, category=category, division=division)
        )
    return competitions


def fetch_season_payload(session: requests.Session, season_id: str) -> dict:
    """Raw call to fetch_season_competitions -- returns the full JSON payload
    (competitions list AND groups_season), so callers can inspect both."""
    data = {
        "seasonID": season_id,
        "pageTitle": "Fixture and Results",
        "lastSegment": "fixture-and-results",
    }
    resp = _post(session, "fetch_season_competitions", data)
    return resp.json()


def parse_groups(payload: dict) -> list[Group]:
    groups = []
    for option_html in payload.get("groups_season", []):
        soup = bs4.BeautifulSoup(option_html, features="html.parser")
        option = soup.find("option")
        if option is None:
            continue
        value = option.get("value", "").strip()
        if not value:
            continue  # skip the "All competitions" placeholder
        slug = (option.get("data-seasonname") or "").strip().lower()
        groups.append(Group(id=value, slug=slug, label=option.text.strip()))
    return groups


def fetch_competitions(session: requests.Session, season_name: str, season_id: str) -> list[Competition]:
    """Get every competition/division available for a given season,
    UNFILTERED (recent seasons include junior/beach/etc. competitions
    alongside NVL ones under this same call). Prefer
    fetch_nvl_competitions() unless you specifically want everything."""
    payload = fetch_season_payload(session, season_id)
    competitions = _options_to_competitions(payload.get("competitions", ""))
    logger.info(f"[{season_name}] Found {len(competitions)} competitions (unfiltered)")
    return competitions


def fetch_competitions_for_group(
    session: requests.Session, season_id: str, group_id: str
) -> list[Competition]:
    """Get divisions scoped to one competition group (e.g. just 'NVL').
    Note: unlike the other admin-ajax actions, this one returns a raw HTML
    fragment, not JSON."""
    data = {
        "seasonidgrp": season_id,
        "fix_compgrpID": group_id,
        "pageTitle": "Fixture and Results",
        "lastSegment": "fixture-and-results",
    }
    resp = _post(session, "fetch_fixture_by_competitiongrp", data)
    return _options_to_competitions(resp.text)


def fetch_nvl_competitions(
    session: requests.Session, season_name: str, season_id: str
) -> list[Competition]:
    """
    Get NVL-relevant divisions for a season, filtering out junior/beach/
    sitting/regional/etc. competitions that recent seasons bundle in
    alongside NVL under the same seasonID.

    Falls back to the unfiltered competitions list if no recognisable
    NVL-like group is found (e.g. older seasons that only ever had NVL +
    Cups, with no other group types to filter out).
    """
    payload = fetch_season_payload(session, season_id)
    groups = parse_groups(payload)
    nvl_groups = [
        g for g in groups if any(s in g.slug for s in NVL_GROUP_SUBSTRINGS)
    ]

    if not groups or not nvl_groups:
        # No group info, or nothing matched our known slugs -- fall back
        # to the plain competitions list (this is expected/fine for older
        # seasons where NVL + Cups was ~everything anyway).
        competitions = _options_to_competitions(payload.get("competitions", ""))
        logger.info(
            f"[{season_name}] No NVL-specific groups found "
            f"(groups seen: {[g.slug or g.label for g in groups]}); "
            f"using unfiltered list of {len(competitions)} competitions"
        )
        return competitions

    all_competitions: list[Competition] = []
    seen_ids = set()
    for group in nvl_groups:
        time.sleep(1.0)
        comps = fetch_competitions_for_group(session, season_id, group.id)
        for c in comps:
            if c.id not in seen_ids:
                seen_ids.add(c.id)
                all_competitions.append(c)
        logger.info(f"[{season_name}] Group '{group.slug}' ({group.label}): {len(comps)} divisions")

    logger.info(
        f"[{season_name}] {len(all_competitions)} NVL-relevant competitions "
        f"(filtered from groups: {[g.slug for g in nvl_groups]})"
    )
    return all_competitions


def fetch_results_raw(session: requests.Session, season_id: str, competition_id: str) -> dict:
    """Fetch the raw JSON payload of results for one competition/season."""
    data = {
        "res_compID": competition_id,
        "seasonID": season_id,
        "pageTitle": "Fixture and Results",
        "lastSegment": "fixture-and-results",
    }
    resp = _post(session, "fetch_results_by_competition", data)
    return resp.json()


def parse_compresults(
    html_fragment: str,
    season: str,
    season_id: str,
    competition: Competition,
) -> list[Match]:
    """Parse the 'Compresults' HTML fragment into a list of Match objects."""
    soup = bs4.BeautifulSoup(html_fragment, features="html.parser")
    matches = []

    for entry in soup.find_all("div"):
        attrs = {k.lower(): v for k, v in entry.attrs.items()}
        if "data-home-team" not in attrs:
            continue  # this div isn't a match entry (e.g. date-header wrapper)

        home = attrs.get("data-home-team", "")
        away = attrs.get("data-away-team", "")
        date_str = attrs.get("data-date", "")

        match = Match(
            season=season,
            season_id=season_id,
            competition_id=competition.id,
            competition_name=competition.name,
            category=competition.category,
            division=competition.division,
            fixture_id=None,
            home=home,
            away=away,
            date_str=date_str,
        )

        # Extract numeric set/point spans (no attrs), same approach as the
        # legacy scraper: [home_sets, away_sets, h1,a1, h2,a2, ...]
        numeric_values = []
        for span in entry.find_all("span"):
            if span.attrs:
                continue
            text = span.text.strip()
            if text.isnumeric():
                numeric_values.append(int(text))
            elif ":" in text:
                label, _, value = text.partition(":")
                label = label.strip().lower()
                value = value.replace("(Pending)", "").strip()
                if label == "referee 1":
                    match.r1 = value
                elif label == "referee 2":
                    match.r2 = value
                elif label == "venue":
                    match.venue = value
                elif label:
                    match.extra[label] = value

        if numeric_values:
            match.home_sets = numeric_values[0]
            match.away_sets = numeric_values[1]
            match.home_points = numeric_values[2::2]
            match.away_points = numeric_values[3::2]

        fmore = entry.find("span", class_="fmore")
        if fmore:
            match.fixture_id = fmore.get("data-fid")

        matches.append(match)

    return matches
