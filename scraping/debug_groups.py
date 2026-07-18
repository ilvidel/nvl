"""
Debug helper for seasons where group filtering is ambiguous (e.g. 2024-2025,
which has no plain "nvl"/"cups" group -- see test_probe.py output).

Dumps every competition found under every group for a given season, so we
can manually confirm which groups actually hold real NVL division data
vs. leftover/test/junior groups.

Usage:
    python debug_groups.py 2024-2025
"""

import sys
import time

from scraper import make_session, fetch_season_payload, parse_groups, fetch_competitions_for_group
from seasons import SEASONS

DELAY_SECONDS = 1.0


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in SEASONS:
        print(f"Usage: python debug_groups.py <season>\nKnown seasons: {sorted(SEASONS)}")
        sys.exit(1)

    season_name = sys.argv[1]
    season_id = SEASONS[season_name]

    session = make_session()
    payload = fetch_season_payload(session, season_id)
    groups = parse_groups(payload)

    print(f"=== {season_name} (seasonID={season_id}): {len(groups)} groups ===\n")

    for group in groups:
        time.sleep(DELAY_SECONDS)
        try:
            comps = fetch_competitions_for_group(session, season_id, group.id)
        except Exception as e:
            print(f"[{group.slug}] '{group.label}' (id={group.id}): ERROR {e}\n")
            continue

        print(f"[{group.slug}] '{group.label}' (id={group.id}): {len(comps)} competitions")
        for c in comps[:30]:
            print(f"    - [{c.id}] {c.name}")
        if len(comps) > 30:
            print(f"    ... and {len(comps) - 30} more")
        print()


if __name__ == "__main__":
    main()
