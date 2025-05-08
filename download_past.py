import argparse
import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select

# Selenium has a packaging problem in Debian, so it must be installed via pip, not apt.
# To do so, create a pyenv and install it in there, then run this using that pyenv
WAIT_TIME = 2


def download(target=None):
    url = "https://competitions.volleyzone.co.uk/fixture-and-results/nvl/"
    browser = webdriver.Firefox()
    browser.get(url)

    results_button = browser.find_element(by="id", value="results-tab")
    results_button.click()
    time.sleep(WAIT_TIME)
    year_select = Select(browser.find_element(by="id", value="select_season"))

    if target:
        seasons = [target]
    else:
        seasons = [x.text for x in year_select.options if "Select" not in x.text]
        print(f"Seasons: {sorted(seasons)}")
        time.sleep(WAIT_TIME)

    # for each season
    for season in sorted(seasons):
        print(f"Processing season {season}...")
        year_select.select_by_visible_text(season)
        time.sleep(WAIT_TIME)

        # find the divisions
        division_select = Select(
            browser.find_element(by="id", value="select_comp_result")
        )
        divisions = [x.text for x in division_select.options if "All" not in x.text]
        print(f"Divisions: {sorted(divisions)}")

        # for each division, get the results
        for division in divisions:
            division_select.select_by_visible_text(division)
            time.sleep(WAIT_TIME)

            print(f"Downloading {season} {division}")
            division = division.replace(" ", "_").lower()
            with open(f"results-{season}-{division}.html", "w") as f:
                f.write(browser.page_source)

    browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "season",
        help="Specific season to download, e.g. '2005-2006'",
        default=None,
        nargs="?",
    )

    args = parser.parse_args()
    download(args.season)
