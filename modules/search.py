"""
modules/search.py  –  Train Search Automation
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.config import JOURNEY
from utils.browser import safe_click, fast_type
from utils.logger import logger


def _fill_station(driver, field_type: str, station_code: str):

    if field_type == "from":
        xpath = "//p-autocomplete[@formcontrolname='origin']//input"
    else:
        xpath = "//p-autocomplete[@formcontrolname='destination']//input"

    field = WebDriverWait(driver,20).until(
        EC.element_to_be_clickable((By.XPATH,xpath))
    )

    field.clear()
    field.send_keys(station_code)

    WebDriverWait(driver,10).until(
        EC.visibility_of_element_located(
            (By.XPATH,"//li[contains(@class,'ui-autocomplete-item')]")
        )
    )

    driver.find_element(
        By.XPATH,
        "(//li[contains(@class,'ui-autocomplete-item')])[1]"
    ).click()

    logger.info(f"{station_code} selected")


def fill_journey_details(driver) -> bool:

    try:

        logger.info("Filling journey form")

        WebDriverWait(driver,20).until(
            EC.presence_of_element_located(
                (By.XPATH,"//p-autocomplete[@formcontrolname='origin']//input")
            )
        )

        # FROM
        _fill_station(driver,"from",JOURNEY["from_station"])

        # TO
        _fill_station(driver,"to",JOURNEY["to_station"])

        # DATE
        date_field = WebDriverWait(driver,20).until(
            EC.element_to_be_clickable(
                (By.XPATH,"//p-calendar[@formcontrolname='journeyDate']//input")
            )
        )

        date_field.clear()
        date_field.send_keys(JOURNEY["date"])
        date_field.send_keys(Keys.TAB)

        logger.info("Date filled")

        # CLASS
        try:

            class_dropdown = WebDriverWait(driver,10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,"//p-dropdown[@formcontrolname='journeyClass']//div[contains(@class,'ui-dropdown')]")
                )
            )

            class_dropdown.click()

            class_option = WebDriverWait(driver,10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,f"//li[@role='option']//span[contains(text(),'{JOURNEY['travel_class']}')]")
                )
            )

            class_option.click()

        except Exception as e:
            logger.warning(f"class selection issue {e}")

        # QUOTA
        try:

            quota_dropdown = WebDriverWait(driver,10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,"//p-dropdown[@formcontrolname='journeyQuota']//div[contains(@class,'ui-dropdown')]")
                )
            )

            quota_dropdown.click()

            quota_option = WebDriverWait(driver,10).until(
                EC.element_to_be_clickable(
                    (By.XPATH,f"//li[@role='option']//span[contains(text(),'{JOURNEY['quota']}')]")
                )
            )

            quota_option.click()

        except Exception as e:
            logger.warning(f"quota selection issue {e}")

        return True

    except Exception as e:

        logger.error(f"Error filling journey details: {e}")
        return False

def click_search(driver) -> bool:

    try:

        search_btn = WebDriverWait(driver,20).until(
            EC.element_to_be_clickable(
                (By.XPATH,"//button[contains(@class,'train_Search')]")
            )
        )

        search_btn.click()

        logger.info("Search clicked")

        time.sleep(4)

        return True

    except TimeoutException:

        logger.error("Search button not found")

        return False


def search_trains(driver) -> bool:

    logger.info("Starting train search")

    # if not fill_journey_details(driver):
    #     return False

    if not click_search(driver):
        return False

    logger.info("Train search submitted")

    return True