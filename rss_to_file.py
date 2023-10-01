from __future__ import annotations

import argparse
import json
import logging
import random
import re
import time
from pathlib import Path
from typing import TypedDict, cast

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from typing_extensions import NotRequired

HTML_DIV_ID = "top_panel"
DOWNLOAD_WAIT = 0.2

RSS_LINK_PATTERN = re.compile(r"&id=([0-9]+)&")
DL_LINK_PATTERN = re.compile(r"\?id=([0-9]+)&")

CONFIG_FOLDER = Path().home() / ".config" / "rss_to_file"
CONFIG_FILE = CONFIG_FOLDER / "config.json"

PAGE_URL_QUERY = "&page={page}"

ITEMS_PER_PAGE = 50
MAX_NUMBER_OF_PAGES = 200
FIRST_PAGE = 0

OLDEST_ID = 672701

GET_ALL = False


class Category(TypedDict):
    name: str
    id: str
    url: str
    last_dled_id: NotRequired[int]


class Config(TypedDict):
    base_url: str
    categories: list[Category]
    rss_url: str
    passkey: str


def get_torrents(
    base_url: str,
    driver: uc.Chrome,
    previous_latest_id: int,
    rss_url: str,
    passkey: str,
) -> int | None:
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait

    latest_id = None

    for page in range(FIRST_PAGE, MAX_NUMBER_OF_PAGES + 1):
        url = base_url.format(page=page * ITEMS_PER_PAGE)
        logging.info("Page: %s", url)
        driver.get(url)

        logging.info("Waiting for page %s to load...", url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, HTML_DIV_ID))
        )

        soup = BeautifulSoup(driver.page_source)
        table_lines = soup.find_all("a", id="get_nfo")
        found_ids = [int(x["target"]) for x in table_lines]
        if not found_ids:
            logging.info("No files found.")
            return None

        latest_id = max(found_ids)

        for found_id in found_ids:
            logging.info(found_id)
            if found_id <= previous_latest_id and not GET_ALL:
                return latest_id
            driver.get(rss_url.format(torrent_id=found_id, passkey=passkey))
            time.sleep(DOWNLOAD_WAIT + random.randint(0, 10) * 0.1)

            driver.get(url)
    return latest_id


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Gather files from RSS flow.")
    parser.add_argument(
        "--config", help="Path to config file", default=CONFIG_FILE, type=Path
    )
    args = parser.parse_args()

    if not (config_path := args.config).exists() and not config_path.is_file():
        if config_path == CONFIG_FILE:
            CONFIG_FOLDER.mkdir(exist_ok=True, parents=True)
            CONFIG_FILE.write_text("{}")
            logging.info("Config file created at %s", CONFIG_FILE)
        else:
            logging.info("Config file %s does not exist.", config_path)
        return

    config = cast(Config, json.loads(config_path.read_text()))
    base_url = config["base_url"]

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={CONFIG_FOLDER}/profile2")
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    driver = uc.Chrome(options=options)

    for category in config.get("categories", []):
        logging.info("Category: %s", category["name"])

        url = base_url + category["url"] + PAGE_URL_QUERY
        rss_url = base_url + config["rss_url"]
        passkey = config["passkey"]

        previous_latest_id = category.get("last_dled_id", 0)

        with driver:
            latest_id = get_torrents(url, driver, previous_latest_id, rss_url, passkey)

        if latest_id is not None:
            category["last_dled_id"] = latest_id

        with config_path.open("w") as f:
            json.dump(config, f, indent=4)

    if __name__ == "__main__":
        main()
