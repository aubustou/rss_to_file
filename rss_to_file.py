import argparse
import time
from pprint import pprint

import undetected_chromedriver.v2 as uc
from bs4 import BeautifulSoup

HTML_DIV_ID = "webkit-xml-viewer-source-xml"
DOWNLOAD_WAIT = 0.2


def main():
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("url", help="URL to RSS")
    args = parser.parse_args()

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
    with driver:
        for url in urls:
            driver.get(url)
            time.sleep(DOWNLOAD_WAIT)


if __name__ == "__main__":
    main()
