"""
modules/payment.py  –  Payment Method Selection
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.config import PAYMENT, AUTOMATION
from utils.browser import wait_for_element, wait_clickable, safe_click, fast_type, wait_for_user
from utils.logger import logger

# XPath patterns for each payment method tab/option
PAYMENT_SELECTORS = {
    "UPI": [
        "//div[contains(text(),'UPI')]",
        "//label[contains(text(),'UPI')]",
        "//span[contains(text(),'UPI')]",
    ],
    "NEFT": [
        "//div[contains(text(),'Net Banking')]",
        "//label[contains(text(),'Net Banking')]",
    ],
    "CARD": [
        "//div[contains(text(),'Credit')]",
        "//div[contains(text(),'Debit')]",
        "//label[contains(text(),'Card')]",
    ],
    "WALLET": [
        "//div[contains(text(),'Wallet')]",
        "//label[contains(text(),'Wallet')]",
    ],
    "IRCTC_WALLET": [
        "//div[contains(text(),'IRCTC eWallet')]",
        "//label[contains(text(),'eWallet')]",
    ],
}


def select_payment_method(driver) -> bool:
    """Click the configured payment method tab."""
    method = PAYMENT.get("method", "UPI").upper()
    selectors = PAYMENT_SELECTORS.get(method, PAYMENT_SELECTORS["UPI"])

    for xpath in selectors:
        try:
            el = wait_clickable(driver, By.XPATH, xpath, timeout=5)
            safe_click(driver, el)
            logger.info(f"Payment method '{method}' selected.")
            time.sleep(1)
            return True
        except TimeoutException:
            continue

    logger.warning(f"Payment tab for '{method}' not found; user must select manually.")
    return True  # non-fatal – user can select on gateway


def fill_upi_id(driver) -> bool:
    """Pre-fill UPI ID if method is UPI."""
    if PAYMENT.get("method", "").upper() != "UPI":
        return True
    upi_id = PAYMENT.get("upi_id", "")
    if not upi_id:
        return True
    try:
        upi_field = wait_for_element(
            driver,
            By.XPATH,
            "//input[contains(@placeholder,'UPI') or contains(@id,'upi')]",
            timeout=8,
        )
        fast_type(upi_field, upi_id)
        logger.info(f"UPI ID '{upi_id}' filled.")

        verify_btn = wait_clickable(
            driver,
            By.XPATH,
            "//button[contains(text(),'Verify') or contains(text(),'VERIFY')]",
            timeout=5,
        )
        safe_click(driver, verify_btn)
        time.sleep(2)
        return True
    except (TimeoutException, NoSuchElementException):
        logger.info("UPI ID field not found on this screen (may appear in gateway).")
        return True


def click_pay_now(driver) -> bool:
    """Click 'Pay & Book' or 'Proceed to Pay'."""
    try:
        pay_btn = wait_clickable(
            driver,
            By.XPATH,
            "//button[contains(text(),'Pay') or contains(text(),'PAY') "
            "or contains(text(),'Proceed') or contains(text(),'PROCEED')]",
            timeout=15,
        )
        safe_click(driver, pay_btn)
        logger.info("Pay button clicked – redirecting to payment gateway.")
        time.sleep(3)
        return True
    except TimeoutException:
        logger.error("Pay button not found.")
        return False


def await_manual_payment(driver) -> bool:
    """Wait for user to complete payment on the gateway."""
    logger.info("─── Payment Gateway ───")
    wait_for_user(
        "Complete the payment in the browser, then press ENTER.",
        timeout=300,  # 5 minutes
    )
    logger.info("User indicated payment step completed.")
    return True


def process_payment(driver) -> bool:
    """Full payment flow."""
    logger.info("─── Starting Payment ───")
    select_payment_method(driver)
    fill_upi_id(driver)
    if not click_pay_now(driver):
        return False
    return await_manual_payment(driver)
