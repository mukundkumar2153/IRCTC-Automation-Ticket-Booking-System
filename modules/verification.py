"""
modules/verification.py  –  CAPTCHA & OTP Handling
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.config import AUTOMATION
from utils.browser import wait_clickable, safe_click, wait_for_user
from utils.logger import logger


def handle_booking_captcha(driver) -> bool:
    """
    Pause for the user to solve the booking-stage CAPTCHA,
    then click 'Continue' / 'Next'.
    """
    logger.info("Waiting for user to solve booking CAPTCHA…")
    solved = wait_for_user(
        "Please solve the CAPTCHA shown in the browser, then press ENTER.",
        timeout=AUTOMATION["captcha_wait"],
    )
    if not solved:
        logger.error("Booking CAPTCHA timed out.")
        return False

    try:
        btn = wait_clickable(
            driver,
            By.XPATH,
            "//button[contains(text(),'CONTINUE') or contains(text(),'Next') or contains(text(),'Proceed')]",
            timeout=10,
        )
        safe_click(driver, btn)
        logger.info("Booking CAPTCHA confirmed.")
        time.sleep(2)
        return True
    except TimeoutException:
        logger.warning("No 'Continue' button found after CAPTCHA – trying to proceed.")
        return True


def handle_otp(driver) -> bool:
    """
    Pause for the user to enter the OTP received on their phone,
    then click 'Submit' / 'Verify'.
    """
    logger.info("Waiting for user to enter OTP…")
    solved = wait_for_user(
        "Enter the OTP received on your registered mobile in the browser, then press ENTER.",
        timeout=AUTOMATION["otp_wait"],
    )
    if not solved:
        logger.error("OTP entry timed out.")
        return False

    try:
        btn = wait_clickable(
            driver,
            By.XPATH,
            "//button[contains(text(),'SUBMIT') or contains(text(),'Verify') or contains(text(),'VERIFY')]",
            timeout=10,
        )
        safe_click(driver, btn)
        logger.info("OTP submitted.")
        time.sleep(3)
        return True
    except TimeoutException:
        logger.warning("No OTP submit button found – assuming OTP auto-submitted.")
        return True


def complete_verification(driver) -> bool:
    """Handle full verification stage: CAPTCHA → OTP."""
    logger.info("─── Verification Stage ───")
    if not handle_booking_captcha(driver):
        return False
    if not handle_otp(driver):
        return False
    logger.info("✅ Verification complete.")
    return True
