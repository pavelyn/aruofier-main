#!/usr/bin/python3.10.4
import ctypes
import datetime
import os
import pathlib
import shutil
import threading
import time

import bs4
import cloudscraper
import dotenv

SOUNDS_DIR = pathlib.Path(__file__).parent.resolve() / "sounds"
SOUND_PATHS = tuple(map(str, SOUNDS_DIR.glob("**/*")))

dotenv.load_dotenv()

NOTIFICATION_VOL = float(os.getenv("NOTIFICATION_VOL", "0.7"))
UPDATE_TIME = 60
ADS_URL = "https://ru.aruodas.lt/butu-nuoma/vilniuje/?FRoomNumMin=2&FRoomNumMax=3&FPriceMax=1500&FBuildYearMin=2005&FRentOnlyRoom=1&FAddDate=1&detailed_search=1&FWarmSystem=thermostat"

scraper = cloudscraper.create_scraper(browser={"custom": "ScraperBot/1.0"})


def play_random_sound() -> None:
    print('Found!!!!!!!!!') # type: ignore


def print_notification(message: object) -> None:
    now = datetime.datetime.now().strftime("%H:%M:%S")
    terminal_width = shutil.get_terminal_size().columns
    print("\033[92m", f"[{now}]", end="", sep="")
    print("\u001b[36m", "New ads!")
    print("\u001b[0m", message, sep="")
    print("\u001b[31;1m", "─" * (terminal_width - 1), "\u001b[0m", sep="")


def get_page_content(url: str) -> str:
    resp = scraper.get(url=url)
    resp.raise_for_status()
    return resp.text  # type: ignore


def get_page_ads(page_content: str) -> list[bs4.Tag]:
    soup = bs4.BeautifulSoup(page_content, "html.parser")
    return soup.find(class_="list-search").tbody.find_all(  # type: ignore
        class_="list-row", style=False
    )


def get_ad_links(adverts: list[bs4.Tag]) -> list[str]:
    links: list[str] = []
    for advert in adverts:
        try:
            link = advert.td.div.a["href"]
        except (TypeError, AttributeError):
            continue
        links.append(link)
    return links


def main() -> None:
    #comtypes.CoInitialize()
    cache: list[str] = []
    while True:
        links = get_ad_links(get_page_ads(get_page_content(ADS_URL)))
        new_links = tuple(
            l for l in links[: len(links) // 2] if l not in cache
        )

        if cache and new_links:
            print_notification("• " + "\n• ".join(new_links))
            play_random_sound(NOTIFICATION_VOL)

        cache = links

        time.sleep(UPDATE_TIME)


if __name__ == "__main__":
    print("Running Aruodas scrapper...")
    threading.Thread(target=main).start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting programm...")
        os._exit(0)
