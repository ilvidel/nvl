"""
Quick sanity check before running the full scrape.

Pulls ONE division's results from a handful of seasons spanning the site's
history (oldest, a couple of middle years, and the current one), saves the
raw JSON responses to disk, and prints a parse summary for each -- flagging
anything that looks like the page format has drifted (missing referee/venue
fields, unrecognised extra labels, unparsed numeric scores, etc.).

Usage:
    cd scraping
    python test_probe.py

Output:
    - Raw JSON responses saved to ../data/raw/<season>_<competition_id>.json
    - A summary printed to stdout for each season/division probed
"""

from __future__ import annotations

import json
import os
import time

from scraper import (
    make_session,
    fetch_season_payload,
    parse_groups,
    fetch_nvl_competitions,
    fetch_results_raw,
    parse_compresults,
)
from seasons import SEASONS

# A spread of seasons to probe: oldest available, a couple of mid-range
# years, and the most recent completed one. Feel free to edit this list.
PROBE_SEASONS = [
    "2005-2006",
    "2015-2016",
    "2020-2021",  # not expected to exist -- tests that we handle this gracefully
    "2024-2025",
    "2025-2026",
]

RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
DELAY_SECONDS = 1.5


def probe_season(session, season_name: str):
    if season_name not in SEASONS:
        print(f"\n=== {season_name}: SKIPPED (not in seasons.SEASONS mapping) ===")
        return

    season_id = SEASONS[season_name]
    print(f"\n=== {season_name} (seasonID={season_id}) ===")

    try:
        payload = fetch_season_payload(session, season_id)
        groups = parse_groups(payload)
        print(f"  Groups found: {[(g.slug, g.label, g.id) for g in groups] or 'none'}")

        unfiltered_count = len(payload.get("competitions", "").split("<option"))  # rough count
        competitions = fetch_nvl_competitions(session, season_name, season_id)
        print(f"  {len(competitions)} NVL-relevant competitions after group filtering "
              f"(unfiltered list had ~{max(unfiltered_count - 1, 0)} options)")

        os.makedirs(RAW_DIR, exist_ok=True)
        season_payload_path = os.path.join(RAW_DIR, f"{season_name}_season_payload.json")
        with open(season_payload_path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"  Saved season payload -> {season_payload_path}")
    except Exception as e:
        print(f"  ERROR fetching competitions: {e}")
        return

    if not competitions:
        print("  No competitions found for this season.")
        return

    print("  Sample:")
    for c in competitions[:5]:
        print(f"    - [{c.id}] {c.name}  (category={c.category!r}, division={c.division!r})")

    # Probe just the first competition in detail
    competition = competitions[0]
    time.sleep(DELAY_SECONDS)
    try:
        raw = fetch_results_raw(session, season_id, competition.id)
    except Exception as e:
        print(f"  ERROR fetching results for {competition.name}: {e}")
        return

    os.makedirs(RAW_DIR, exist_ok=True)
    raw_path = os.path.join(RAW_DIR, f"{season_name}_{competition.id}.json")
    with open(raw_path, "w") as f:
        json.dump(raw, f, indent=2)
    print(f"  Saved raw response -> {raw_path}")

    html_fragment = raw.get("Compresults", "")
    if not html_fragment.strip():
        print(f"  WARNING: empty 'Compresults' field for {competition.name}. "
              f"Keys present in response: {list(raw.keys())}")
        return

    matches = parse_compresults(html_fragment, season_name, season_id, competition)
    print(f"  Parsed {len(matches)} matches for '{competition.name}'")

    if not matches:
        print("  WARNING: 0 matches parsed despite non-empty response -- "
              "the div structure may have changed. Raw HTML snippet:")
        print("  " + html_fragment[:500].replace("\n", " "))
        return

    # Flag anomalies across all parsed matches in this division
    missing_venue = sum(1 for m in matches if not m.venue)
    missing_both_refs = sum(1 for m in matches if not m.r1 and not m.r2)
    missing_sets = sum(1 for m in matches if m.home_sets is None)
    unexpected_labels = set()
    for m in matches:
        unexpected_labels.update(m.extra.keys())

    print(f"    - missing venue:        {missing_venue}/{len(matches)}")
    print(f"    - missing both referees: {missing_both_refs}/{len(matches)}")
    print(f"    - missing set scores:    {missing_sets}/{len(matches)}")
    print(f"    - unrecognised extra labels seen: {sorted(unexpected_labels) or 'none'}")

    sample = matches[0]
    print(f"    - sample match: {sample.home} vs {sample.away} on {sample.date_str}")
    print(f"      sets={sample.home_sets}-{sample.away_sets} "
          f"r1={sample.r1!r} r2={sample.r2!r} venue={sample.venue!r} "
          f"fixture_id={sample.fixture_id!r} extra={sample.extra}")


def main():
    session = make_session()
    for season_name in PROBE_SEASONS:
        probe_season(session, season_name)
        time.sleep(DELAY_SECONDS)

    print("\nDone. Please paste the full output above back to Claude, "
          "along with the contents of any saved files in data/raw/ that "
          "look unusual (e.g. 0 matches parsed, unrecognised labels).")


if __name__ == "__main__":
    main()
