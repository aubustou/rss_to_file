import argparse
import json
from json.decoder import JSONDecodeError
import time
from pathlib import Path
from random import randint

import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup

API_KEY = ""

SUBCATEGORY_ID = "2152"
URL = f"https://www5.yggtorrent.fi/engine/search?name=&description=&file=&uploader=&category=2140&sub_category={SUBCATEGORY_ID}&do=search&page="

INDEX = 0
NUMBER_OF_RESULTS_PER_PAGE = 50
MAX_PAGES = 14

LAST_DLED_ID_FOLDER = Path().home() / ".config" / "rss_to_file"

def main():
    parser = argparse.ArgumentParser(description="Gather files from RSS flow.")

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait

    LAST_DLED_ID_FOLDER.mkdir(exist_ok=True)
    last_dled_id_file = LAST_DLED_ID_FOLDER / SUBCATEGORY_ID
    last_dled_id_file.touch()

    full_ids = set()
    if (path := Path("ids")).exists():
        try:
            ids = json.load(path.open())
        except JSONDecodeError:
            ids = set()
    else:
        path.touch()
        ids = set()

    driver = uc.Chrome()

    with driver:
        # driver.get(URL + str(0))
        # WebDriverWait(driver, 20).until(
        #     EC.presence_of_element_located((By.ID, "get_nfo"))
        # )
        for page_index in range(INDEX, (MAX_PAGES * NUMBER_OF_RESULTS_PER_PAGE)+ 1, NUMBER_OF_RESULTS_PER_PAGE):
            driver.get(URL + str(page_index))

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "get_nfo"))
            )

            source = driver.page_source

            Path("toto").write_text(source)

            soup = BeautifulSoup(source, features="html.parser")
            ids = {
                x.get("target")
                for x in soup.body.find_all("a")
                if x.get("id") == "get_nfo"
            }
            print(ids)

            full_ids = full_ids.union(ids)

        for id_ in full_ids:
            print(id_)
            driver.get(
                f"https://www5.yggtorrent.fi/rss/download?id={id_}&passkey={API_KEY}"
            )
            time.sleep(randint(1, 10) * 0.1)

    with path.open("w") as fp:
        json.dump(list(full_ids), fp)

    last_dled_id_file.write_text(str(max((int(x) for x in full_ids))))


if __name__ == "__main__":
    main()
