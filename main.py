#!/usr/bin/env python3
"""
main.py  –  IRCTC Ticket Booking Automation Assistant
Run: python main.py
"""
import sys
import time

from utils.browser import create_driver
from utils.logger import logger

from modules.login        import login
from modules.search       import search_trains
from modules.selection    import select_train
from modules.passengers   import fill_passenger_details
from modules.verification import complete_verification
from modules.payment      import process_payment
from modules.confirmation import capture_confirmation


def run():
    driver = None
    try:
        logger.info("╔══════════════════════════════════════════╗")
        logger.info("║   IRCTC Booking Automation – Starting    ║")
        logger.info("╚══════════════════════════════════════════╝")

        driver = create_driver()

        # ── Step 1: Login ──────────────────────────────────────────────────────
        if not login(driver):
            logger.error("Login failed. Exiting.")
            return 1

        # ── Step 2: Search Trains ──────────────────────────────────────────────
        if not search_trains(driver):
            logger.error("Train search failed. Exiting.")
            return 1

        # ── Step 3: Select Train ───────────────────────────────────────────────
        if not select_train(driver):
            logger.error("Train selection failed. Exiting.")
            return 1

        # ── Step 4: Passenger Details ──────────────────────────────────────────
        if not fill_passenger_details(driver):
            logger.error("Passenger form failed. Exiting.")
            return 1

        # ── Step 5: Verification (CAPTCHA + OTP) ──────────────────────────────
        if not complete_verification(driver):
            logger.error("Verification failed. Exiting.")
            return 1

        # ── Step 6: Payment ────────────────────────────────────────────────────
        if not process_payment(driver):
            logger.error("Payment step failed. Exiting.")
            return 1

        # ── Step 7: Confirmation ───────────────────────────────────────────────
        capture_confirmation(driver)

        logger.info("╔══════════════════════════════════════════╗")
        logger.info("║   Booking Automation Complete ✅          ║")
        logger.info("╚══════════════════════════════════════════╝")
        return 0

    except KeyboardInterrupt:
        logger.info("User cancelled booking.")
        return 130

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1

    finally:
        if driver:
            input("\nPress ENTER to close the browser…")
            driver.quit()
            logger.info("Browser closed.")


if __name__ == "__main__":
    sys.exit(run())
