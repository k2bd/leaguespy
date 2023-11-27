import time
from contextlib import contextmanager
from typing import Generator

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from leaguespy.player_task_info import PlayerTaskInfo

TASKS_PAGE = "https://oldschool.runescape.wiki/w/Trailblazer_Reloaded_League/Tasks"
SEARCH_BOX_ID = "ooui-1"
BUTTON_CLASS_NAME = "oo-ui-buttonElement-button"
POST_CLICK_SLEEP_TIME_S = 2


@contextmanager
def chrome_driver() -> Generator[webdriver.Chrome, None, None]:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-images")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )

    try:
        yield driver
    finally:
        driver.quit()


def parse_stats_page(page_html: str) -> list[PlayerTaskInfo]:
    soup = BeautifulSoup(page_html, "html.parser")

    tasks = soup.find_all("tr", attrs={"data-taskid": True})

    results: list[PlayerTaskInfo] = []

    for task in tasks:
        task_id = int(task["data-taskid"])
        region = str(task["data-tbz-area-for-filtering"])
        description = str(task.find_all("td")[1].text.strip())
        point = int(task.find_all("td")[4].text.strip())
        completion_percent = task.find_all("td")[5].text.strip()
        player_completed = "highlight-on" in task.get("class", [])

        results.append(
            PlayerTaskInfo(
                task_id=task_id,
                region=region,
                description=description,
                points=point,
                completion_pct=completion_percent,
                player_completed=player_completed,
            )
        )

    return results


def get_player_stats(player_name: str) -> list[PlayerTaskInfo]:
    with chrome_driver() as driver:
        driver.get(TASKS_PAGE)

        driver.implicitly_wait(10)

        search_box = driver.find_element(by=By.ID, value=SEARCH_BOX_ID)
        search_button = driver.find_element(by=By.CLASS_NAME, value=BUTTON_CLASS_NAME)

        search_box.send_keys(player_name)
        search_button.click()

        time.sleep(POST_CLICK_SLEEP_TIME_S)

        page_html = driver.page_source

    return parse_stats_page(page_html)
