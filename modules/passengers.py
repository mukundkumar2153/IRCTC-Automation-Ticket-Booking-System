"""
modules/passengers.py  –  Passenger Details Form Automation
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.config import PASSENGERS, AUTOMATION
from utils.browser import wait_for_element, wait_clickable, safe_click, fast_type, slow_type
from utils.logger import logger

_fill = fast_type if AUTOMATION.get("tatkal_mode") else slow_type


def _select_dropdown_option(driver, dropdown_xpath: str, value: str):
    """Select an option by visible text or value in a <select> or p-dropdown."""
    try:
        el = driver.find_element(By.XPATH, dropdown_xpath)
        tag = el.tag_name.lower()
        if tag == "select":
            Select(el).select_by_visible_text(value)
        else:
            safe_click(driver, el)
            time.sleep(0.3)
            option = driver.find_element(
                By.XPATH,
                f"//li[contains(.,'{value}') or @label='{value}']",
            )
            safe_click(driver, option)
    except Exception as e:
        logger.warning(f"Dropdown '{dropdown_xpath}' → '{value}' failed: {e}")


def fill_single_passenger(driver, idx: int, pax: dict):
    """Fill one passenger row (0-indexed)."""
    logger.info(f"Filling passenger {idx+1}: {pax['name']}")

    # ── Name ──────────────────────────────────────────────────────────────────
    name_field = wait_for_element(
        driver,
        By.XPATH,
        f"(//input[contains(@placeholder,'Passenger Name') or @id='psgName'])[{idx+1}]",
    )
    _fill(name_field, pax["name"])

    # ── Age ───────────────────────────────────────────────────────────────────
    age_field = driver.find_element(
        By.XPATH,
        f"(//input[contains(@placeholder,'Age') or @id='age'])[{idx+1}]",
    )
    _fill(age_field, str(pax["age"]))

    # ── Gender ────────────────────────────────────────────────────────────────
    _select_dropdown_option(
        driver,
        f"(//p-dropdown[contains(@id,'gender')] | //select[contains(@id,'gender')])[{idx+1}]",
        {"M": "Male", "F": "Female", "T": "Transgender"}.get(pax["gender"], "Male"),
    )

    # ── Berth Preference ──────────────────────────────────────────────────────
    try:
        _select_dropdown_option(
            driver,
            f"(//p-dropdown[contains(@id,'berth')] | //select[contains(@id,'berth')])[{idx+1}]",
            pax.get("berth_preference", "NO"),
        )
    except Exception:
        pass  # Berth preference not always available

    # ── Food Preference ───────────────────────────────────────────────────────
    food = pax.get("food_preference", "")
    if food:
        try:
            food_el = driver.find_element(
                By.XPATH,
                f"(//input[@type='checkbox' and contains(@id,'food')])[{idx+1}]",
            )
            if food.upper() in ("VEG", "NON-VEG") and not food_el.is_selected():
                safe_click(driver, food_el)
        except NoSuchElementException:
            pass

    time.sleep(0.3)


def fill_passengers(driver) -> bool:
    """Fill all configured passengers."""
    logger.info("─── Filling Passenger Details ───")
    try:
        # Wait for the passenger form to appear
        wait_for_element(
            driver,
            By.XPATH,
            "//input[contains(@placeholder,'Passenger Name') or @id='psgName']",
            timeout=20,
        )

        for idx, pax in enumerate(PASSENGERS):
            fill_single_passenger(driver, idx, pax)

        return True
    except Exception as e:
        logger.error(f"Error filling passengers: {e}")
        return False


def click_continue(driver) -> bool:
    """Click 'Continue Booking'."""
    try:
        btn = wait_clickable(
            driver,
            By.XPATH,
            "//button[contains(text(),'Continue') or contains(text(),'CONTINUE')]",
            timeout=10,
        )
        safe_click(driver, btn)
        logger.info("'Continue Booking' clicked.")
        time.sleep(2)
        return True
    except TimeoutException:
        logger.error("'Continue Booking' button not found.")
        return False


def fill_passenger_details(driver) -> bool:
    """Full passenger details flow."""
    if not fill_passengers(driver):
        return False
    return click_continue(driver)
