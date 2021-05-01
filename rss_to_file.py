import argparse
import random
import re
import time
from pathlib import Path
from pprint import pprint

import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup

HTML_DIV_ID = "webkit-xml-viewer-source-xml"
DOWNLOAD_WAIT = 0.2

RSS_LINK_PATTERN = re.compile(r"&id=([0-9]+)&")
DL_LINK_PATTERN = re.compile(r"\?id=([0-9]+)&")

LAST_DLED_ID_FOLDER = Path().home() / ".config" /"rss_to_file"

def main():
    parser = argparse.ArgumentParser(description="Gather files from RSS flow.")
    parser.add_argument("url", help="URL to RSS")
    args = parser.parse_args()

    category_id = RSS_LINK_PATTERN.search(args.url).groups()[0]

    LAST_DLED_ID_FOLDER.mkdir(exist_ok=True)
    last_dled_id_file = LAST_DLED_ID_FOLDER / category_id
    last_dled_id_file.touch()

    driver = uc.Chrome()

    with driver:
        driver.get(args.url)

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, HTML_DIV_ID))
    )

    soup = BeautifulSoup(driver.page_source)
    enclosures = soup.body.div.find_all("enclosure")

    urls = [x.get("url") for x in enclosures]
    pprint(urls)

    content = last_dled_id_file.read_text()
    previous_latest_id = int(content or 0)
    latest_id = None

    with driver:
        for index, url in enumerate(urls):
            match = DL_LINK_PATTERN.search(url)
            current_id = int(match.groups()[0])
            if index == 0:
                latest_id = int(current_id)
            if current_id <= previous_latest_id:
                break
            driver.get(url)
            time.sleep(DOWNLOAD_WAIT + random.randint(0,10)*0.1)

    if latest_id is not None:
        last_dled_id_file.write_text(str(latest_id))


if __name__ == "__main__":
    main()
