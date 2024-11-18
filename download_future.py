from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from game import DIVISIONS

# Selenium has a packaging problem in Debian, so it must be installed via pip, not apt.
# To do so, create a pyenv and install it in there, then run this using that pyenv

url = "https://competitions.volleyzone.co.uk/fixture-and-results/nvl/"
driver = webdriver.Firefox()
driver.get(url)

button = driver.find_element(by='id', value='fixtures-tab')
button.click()
time.sleep(4)

select = Select(driver.find_element(by='id', value='select_comp'))

for cat_id, category in DIVISIONS.items():
    select.select_by_value(cat_id)
    time.sleep(4)

    print(f"Downloading {category}")
    category = category.replace(" ", "_").lower()
    with open(f"{category}.html", "w") as f:
        f.write(driver.page_source)

driver.close()
