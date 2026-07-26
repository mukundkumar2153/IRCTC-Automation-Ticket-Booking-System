# =============================================================================
# IRCTC Booking Assistant - Configuration
# =============================================================================

# ── Credentials ──────────────────────────────────────────────────────────────
CREDENTIALS = {
    "username": "Enter Your IRCTC UserID",
    "password": "Enter Your IRCTC PassWord",
}

# ── Journey Details ───────────────────────────────────────────────────────────
JOURNEY = {
    "from_station": "LTT",          # Station code, e.g. NDLS, BCT, MAS
    "to_station":   "DNR",
    "date":         "04/09/2026",    # DD/MM/YYYY
    "travel_class": "3A",            # SL | 3A | 2A | 1A | CC | EC | 2S
    "quota":        "GN",            # GN (General) | TQ (Tatkal) | PT (Premium Tatkal)
    "preferred_trains": ["13202","12141"],   # e.g. ["12951", "12953"]  – empty = pick first available
}

# ── Passengers ────────────────────────────────────────────────────────────────
PASSENGERS = [
    {
        "name":             "Mukund Kumar",
        "age":              20,
        "gender":           "M",          # M | F | T
        "berth_preference": "SL",         # LB | MB | UB | SL | SU | WS | NO
        "food_preference":  "NO",        # VEG | NON-VEG | NO
        "nationality":      "Indian",
    },
    # Add more passengers as needed (max 6 per booking)
]

# ── Payment ───────────────────────────────────────────────────────────────────
PAYMENT = {
    "method": "UPI",                 # UPI | NEFT | CARD | WALLET | IRCTC_WALLET
    "upi_id": "mukund@bol(Fack)-Enter Your UPI id",      # Required only when method = UPI
}

# ── Automation Behaviour ──────────────────────────────────────────────────────
AUTOMATION = {
    "headless":            False,     # True = no browser window (NOT recommended for CAPTCHA)
    "implicit_wait":       10,        # seconds
    "page_load_timeout":   30,        # seconds
    "captcha_wait":        60,        # seconds user has to solve CAPTCHA
    "otp_wait":            90,        # seconds user has to enter OTP
    "tatkal_mode":         False,     # Enable hyper-fast filling for Tatkal windows
    "auto_retry":          True,      # Retry automatically if seats unavailable
    "max_retries":         5,
    "retry_interval":      10,        # seconds between retries
}

# ── Notifications ─────────────────────────────────────────────────────────────
NOTIFICATIONS = {
    "enabled":       True,
    "email":         "Enter Your Email ID",
    "smtp_host":     "smtp.gmail.com",
    "smtp_port":     587,
    "smtp_user":     "Email ID",
    "smtp_password": "App Password",
}

# ── Paths ─────────────────────────────────────────────────────────────────────
import os
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR      = os.path.join(BASE_DIR, "logs")
DATA_DIR     = os.path.join(BASE_DIR, "data")
BOOKING_FILE = os.path.join(DATA_DIR, "bookings.json")

# ── IRCTC URLs ────────────────────────────────────────────────────────────────
URLS = {
    "home":  "https://www.irctc.co.in/nget/train-search",
    "login": "https://www.irctc.co.in/nget/train-search",
}
