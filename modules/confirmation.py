"""
modules/confirmation.py  –  PNR capture, booking save & notification
"""
import json
import os
import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.config import BOOKING_FILE, DATA_DIR, NOTIFICATIONS, JOURNEY, PASSENGERS
from utils.logger import logger


# ── PNR Extraction ────────────────────────────────────────────────────────────

def extract_pnr(driver) -> str | None:
    """Try multiple strategies to find PNR on the confirmation page."""
    strategies = [
        # Direct element
        lambda d: d.find_element(By.XPATH, "//*[contains(@class,'pnr') and string-length(text())=10]").text,
        lambda d: d.find_element(By.XPATH, "//strong[contains(text(),'PNR')]/following-sibling::*[1]").text,
        lambda d: d.find_element(By.XPATH, "//*[@id='pnrPrint']").text,
        # Regex scan the whole page
        lambda d: re.search(r"PNR[:\s#]*([0-9]{10})", d.page_source).group(1) if re.search(r"PNR[:\s#]*([0-9]{10})", d.page_source) else None,
    ]
    for fn in strategies:
        try:
            result = fn(driver)
            if result:
                return str(result).strip()
        except Exception:
            continue
    return None


def wait_for_confirmation(driver, timeout: int = 60) -> bool:
    """Wait for the booking confirmation / PNR page."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.any_of(
                EC.url_contains("bookingConfirm"),
                EC.url_contains("pnr"),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Booking Confirmed')]")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'PNR')]")),
            )
        )
        logger.info("Confirmation page detected.")
        return True
    except TimeoutException:
        logger.warning("Confirmation page not detected within timeout.")
        return False


# ── Save Booking ──────────────────────────────────────────────────────────────

def save_booking(pnr: str, driver=None) -> dict:
    """Persist booking details to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    booking = {
        "pnr":        pnr,
        "timestamp":  datetime.now().isoformat(),
        "from":       JOURNEY["from_station"],
        "to":         JOURNEY["to_station"],
        "date":       JOURNEY["date"],
        "class":      JOURNEY["travel_class"],
        "quota":      JOURNEY["quota"],
        "passengers": [p["name"] for p in PASSENGERS],
        "url":        driver.current_url if driver else "",
    }

    existing = []
    if os.path.exists(BOOKING_FILE):
        try:
            with open(BOOKING_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except (json.JSONDecodeError, IOError):
            existing = []

    existing.append(booking)
    with open(BOOKING_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    logger.info(f"Booking saved to {BOOKING_FILE}")
    return booking


# ── Notification ──────────────────────────────────────────────────────────────

def send_email_notification(booking: dict):
    """Send a simple email notification after booking."""
    if not NOTIFICATIONS.get("enabled"):
        return
    try:
        import smtplib
        from email.mime.text import MIMEText

        body = (
            f"✅ IRCTC Booking Confirmed!\n\n"
            f"PNR      : {booking['pnr']}\n"
            f"Route    : {booking['from']} → {booking['to']}\n"
            f"Date     : {booking['date']}\n"
            f"Class    : {booking['class']}\n"
            f"Quota    : {booking['quota']}\n"
            f"Passengers: {', '.join(booking['passengers'])}\n"
        )
        msg = MIMEText(body)
        msg["Subject"] = f"Booking Confirmed – PNR {booking['pnr']}"
        msg["From"]    = NOTIFICATIONS["smtp_user"]
        msg["To"]      = NOTIFICATIONS["email"]

        with smtplib.SMTP(NOTIFICATIONS["smtp_host"], NOTIFICATIONS["smtp_port"]) as s:
            s.starttls()
            s.login(NOTIFICATIONS["smtp_user"], NOTIFICATIONS["smtp_password"])
            s.send_message(msg)

        logger.info(f"Notification email sent to {NOTIFICATIONS['email']}.")
    except Exception as e:
        logger.warning(f"Email notification failed: {e}")


def print_confirmation(booking: dict):
    """Pretty-print booking confirmation to console."""
    print("\n" + "═"*60)
    print("  🎟️  BOOKING CONFIRMED!")
    print("═"*60)
    print(f"  PNR Number  : {booking['pnr']}")
    print(f"  From        : {booking['from']}")
    print(f"  To          : {booking['to']}")
    print(f"  Date        : {booking['date']}")
    print(f"  Class       : {booking['class']}")
    print(f"  Quota       : {booking['quota']}")
    print(f"  Passengers  : {', '.join(booking['passengers'])}")
    print(f"  Booked at   : {booking['timestamp']}")
    print("═"*60 + "\n")


# ── Main entry ────────────────────────────────────────────────────────────────

def capture_confirmation(driver) -> bool:
    """Full confirmation capture flow."""
    logger.info("─── Capturing Confirmation ───")
    wait_for_confirmation(driver)
    time.sleep(2)

    pnr = extract_pnr(driver)
    if pnr:
        logger.info(f"✅ PNR captured: {pnr}")
    else:
        logger.warning("PNR could not be extracted automatically.")
        pnr = "UNKNOWN"

    booking = save_booking(pnr, driver)
    print_confirmation(booking)
    send_email_notification(booking)
    return True
