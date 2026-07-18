"""
Mapping of human-readable season names to the site's internal seasonID,
as used by the wp-admin/admin-ajax.php endpoints on
https://competitions.volleyzone.co.uk/fixture-and-results/

Extracted directly from the <select id="select_season"> dropdown.
"""

SEASONS = {
    "2026-2027": "4013",
    "2025-2026": "3852",
    "2024-2025": "3422",
    "2023-2024": "3346",
    "2022-2023": "3301",
    "2021-2022": "3333",
    "2019-2020": "3331",
    "2018-2019": "3330",
    "2017-2018": "3329",
    "2016-2017": "3328",
    "2015-2016": "3327",
    "2014-2015": "3326",
    "2013-2014": "3325",
    "2012-2013": "3324",
    "2011-2012": "3323",
    "2010-2011": "3322",
    "2009-2010": "3321",
    "2008-2009": "3320",
    "2007-2008": "3319",
    "2006-2007": "3318",
    "2005-2006": "3317",
}

# Note: there is no 2020-2021 entry -- the site's dropdown skips it
# (presumably the season was voided/cancelled, e.g. due to COVID).
