from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time

from game import DIVISIONS

# Selenium has a packaging problem in Debian, so it must be installed via pip, not apt.
# To do so, create a pyenv and install it in there, then run this using that pyenv
WAIT_TIME = 2

url = "https://competitions.volleyzone.co.uk/fixture-and-results/nvl/"
browser = webdriver.Firefox()
browser.get(url)

results_button = browser.find_element(by='id', value='results-tab')
results_button.click()
time.sleep(WAIT_TIME)

year_select = Select(browser.find_element(by='id', value='select_season'))
seasons = [x.text for x in year_select.options if "Select" not in x.text]
print(f"Seasons: {sorted(seasons)}")
time.sleep(WAIT_TIME)

# for each season
for season in sorted(seasons):
    print(f"Processing season {season}...")
    year_select.select_by_visible_text(season)
    time.sleep(WAIT_TIME)

    # find the divisions
    division_select = Select(browser.find_element(by='id', value='select_comp_result'))
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