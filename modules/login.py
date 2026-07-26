"""
modules/login.py  –  IRCTC Login Automation
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.config import CREDENTIALS, AUTOMATION, URLS
from utils.browser import wait_for_element, wait_clickable, safe_click, slow_type, wait_for_user
from utils.logger import logger


def open_irctc(driver) -> bool:
    """Navigate to IRCTC home page."""
    try:
        logger.info("Opening IRCTC website…")
        driver.get(URLS["home"])
        time.sleep(2)
        return True
    except Exception as e:
        logger.error(f"Failed to open IRCTC: {e}")
        return False


def click_login_button(driver) -> bool:
    """Click the LOGIN button on the navbar."""
    try:
        login_btn = wait_clickable(driver, By.XPATH, "//a[contains(text(),'LOGIN') or @label='LOGIN']", timeout=15)
        safe_click(driver, login_btn)
        logger.info("Clicked LOGIN button.")
        time.sleep(1.5)
        return True
    except TimeoutException:
        logger.error("LOGIN button not found on page.")
        return False


def fill_credentials(driver) -> bool:
    """Fill username and password fields."""
    try:
        username_field = wait_for_element(driver, By.XPATH, "//input[@placeholder='User Name' or @id='userId']")
        slow_type(username_field, CREDENTIALS["username"])
        logger.info("Username entered.")

        password_field = wait_for_element(driver, By.XPATH, "//input[@type='password' and (@placeholder='Password' or @id='pwd')]")
        slow_type(password_field, CREDENTIALS["password"])
        logger.info("Password entered.")
        return True
    except Exception as e:
        logger.error(f"Failed to fill credentials: {e}")
        return False


def handle_captcha(driver) -> bool:
    """Pause and let user solve CAPTCHA, then click SIGN IN."""
    logger.info("Waiting for user to solve CAPTCHA…")
    wait_for_user(
        "Please solve the CAPTCHA in the browser, then press ENTER.",
        timeout=AUTOMATION["captcha_wait"],
    )

    try:
        sign_in_btn = wait_clickable(
            driver,
            By.XPATH,
            "//button[contains(text(),'SIGN IN') or contains(text(),'Login') or @label='SIGN IN']",
            timeout=10,
        )
        safe_click(driver, sign_in_btn)
        logger.info("SIGN IN clicked after CAPTCHA.")
        time.sleep(3)
        return True
    except TimeoutException:
        logger.error("SIGN IN button not found after CAPTCHA.")
        return False


def verify_login(driver) -> bool:
    """Confirm successful login by checking for username display or dashboard element."""
    try:
        WebDriverWait(driver, 15).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//span[@class='loginusername']")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class,'user-name')]")),
                EC.url_contains("nget/train-search"),
            )
        )
        # Dismiss any post-login popup
        try:
            popup_close = driver.find_element(By.XPATH, "//button[contains(text(),'×') or @class='close']")
            popup_close.click()
        except Exception:
            pass
        logger.info("✅ Login successful!")
        return True
    except TimeoutException:
        logger.error("Login verification failed – check credentials or CAPTCHA.")
        return False


def login(driver) -> bool:
    """Full login flow."""
    logger.info("─── Starting Login ───")
    steps = [
        open_irctc,
        click_login_button,
        fill_credentials,
        handle_captcha,
        verify_login,
    ]
    for step in steps:
        if not step(driver):
            logger.error(f"Login step failed: {step.__name__}")
            return False
    return True
