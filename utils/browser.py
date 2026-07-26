"""
utils/browser.py  –  WebDriver factory & helper methods
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    USE_WDM = True
except ImportError:
    USE_WDM = False

from config.config import AUTOMATION
from utils.logger import logger


def create_driver() -> webdriver.Chrome:
    """Initialise and return a Chrome WebDriver."""
    options = Options()

    if AUTOMATION["headless"]:
        options.add_argument("--headless=new")

    # Performance & stealth options
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    if USE_WDM:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    # Patch navigator.webdriver flag
    driver.execute_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
    driver.implicitly_wait(AUTOMATION["implicit_wait"])
    driver.set_page_load_timeout(AUTOMATION["page_load_timeout"])
    logger.info("Browser launched successfully.")
    return driver


# ── Helper wrappers ───────────────────────────────────────────────────────────

def wait_for_element(driver, by, selector, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )


def wait_clickable(driver, by, selector, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )


def safe_click(driver, element):
    """Scroll into view, then JS-click to bypass overlay issues."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    time.sleep(0.2)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def slow_type(element, text: str, delay: float = 0.05):
    """Type text character-by-character to mimic human speed."""
    element.clear()
    for ch in str(text):
        element.send_keys(ch)
        time.sleep(delay)


def fast_type(element, text: str):
    """Fast fill – used in Tatkal mode."""
    element.clear()
    element.send_keys(str(text))


def wait_for_user(prompt: str, timeout: int = 60) -> bool:
    """
    Print a prompt and wait for the user to press ENTER.
    Returns True when user confirms, False on timeout.
    """
    print(f"\n{'='*60}")
    print(f"  ⚠️  USER ACTION REQUIRED")
    print(f"  {prompt}")
    print(f"  You have {timeout} seconds.")
    print(f"{'='*60}")
    import threading

    confirmed = [False]

    def _ask():
        input("  ▶  Press ENTER when done... ")
        confirmed[0] = True

    t = threading.Thread(target=_ask, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if not confirmed[0]:
        logger.warning("User action timed out.")
    return confirmed[0]
