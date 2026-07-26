# 🚆 IRCTC Ticket Booking Automation Assistant

A semi-automated, modular Python + Selenium assistant that speeds up
IRCTC train ticket booking while keeping humans in the loop for
CAPTCHA, OTP, and payment.

---

## 📁 Project Structure

```
irctc_bot/
├── main.py                  ← Entry point – run this
├── requirements.txt
├── config/
│   └── config.py            ← All settings (credentials, journey, passengers)
├── modules/
│   ├── login.py             ← Step 1 – Login
│   ├── search.py            ← Step 2 – Train Search
│   ├── selection.py         ← Step 3 – Train Selection
│   ├── passengers.py        ← Step 4 – Passenger Details
│   ├── verification.py      ← Step 5 – CAPTCHA & OTP
│   ├── payment.py           ← Step 6 – Payment
│   └── confirmation.py      ← Step 7 – PNR Capture & Save
├── utils/
│   ├── browser.py           ← WebDriver factory & helpers
│   └── logger.py            ← Logging setup
├── logs/                    ← Auto-created session log files
└── data/
    └── bookings.json        ← Auto-created booking history
```

---

## ⚙️ Prerequisites

| Requirement | Version  |
|-------------|----------|
| Python      | ≥ 3.11   |
| Chrome      | Latest   |
| ChromeDriver| Auto-managed via `webdriver-manager` |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure your details
Open `config/config.py` and fill in:

```python
# Credentials
CREDENTIALS = {
    "username": "YOUR_IRCTC_USERNAME",
    "password": "YOUR_IRCTC_PASSWORD",
}

# Journey
JOURNEY = {
    "from_station": "NDLS",
    "to_station":   "BCT",
    "date":         "15/08/2025",   # DD/MM/YYYY
    "travel_class": "3A",
    "quota":        "GN",
}

# Passengers
PASSENGERS = [
    {"name": "Your Name", "age": 28, "gender": "M",
     "berth_preference": "LB", "food_preference": "VEG"},
]

# Payment
PAYMENT = {"method": "UPI", "upi_id": "yourname@upi"}
```

### 3. Run
```bash
cd irctc_bot
python main.py
```

---

## 🔄 Booking Workflow

```
[Bot]  Opens IRCTC website
[Bot]  Fills username & password
[USER] Solves CAPTCHA → presses ENTER
[Bot]  Clicks SIGN IN
[Bot]  Fills From / To / Date / Class / Quota
[Bot]  Clicks Search
[Bot]  Selects preferred or first-available train
[Bot]  Clicks Book Now
[Bot]  Fills all passenger details
[Bot]  Clicks Continue Booking
[USER] Solves booking CAPTCHA → presses ENTER
[USER] Enters OTP → presses ENTER
[Bot]  Selects payment method & fills UPI ID
[Bot]  Clicks Pay & Book
[USER] Completes payment → presses ENTER
[Bot]  Captures PNR, saves to data/bookings.json
[Bot]  Prints confirmation & sends email (optional)
```

---

## ⚡ Tatkal Mode

In `config.py` set:
```python
AUTOMATION = {
    "tatkal_mode": True,
    ...
}
JOURNEY = {
    "quota": "TQ",   # TQ = Tatkal, PT = Premium Tatkal
    ...
}
```
Tatkal mode switches all form filling to `fast_type` (no per-character
delays) for maximum speed during the narrow booking window.

---

## 🔁 Auto Retry

If seats are unavailable, the bot automatically refreshes the results
page and retries:
```python
AUTOMATION = {
    "auto_retry":     True,
    "max_retries":    5,
    "retry_interval": 10,   # seconds
}
```

---

## 📧 Email Notifications

```python
NOTIFICATIONS = {
    "enabled":       True,
    "email":         "you@example.com",
    "smtp_host":     "smtp.gmail.com",
    "smtp_port":     587,
    "smtp_user":     "sender@gmail.com",
    "smtp_password": "YOUR_APP_PASSWORD",   # Use Gmail App Password
}
```

---

## 📊 Booking History

Every successful booking is appended to `data/bookings.json`:
```json
[
  {
    "pnr": "1234567890",
    "timestamp": "2025-08-15T10:30:00",
    "from": "NDLS",
    "to": "BCT",
    "date": "15/08/2025",
    "class": "3A",
    "quota": "GN",
    "passengers": ["Rahul Sharma"]
  }
]
```

---

## ⚠️ Important Notes

1. **CAPTCHA & OTP** are intentionally left to the user – automation of
   these is against IRCTC's Terms of Service and legally restricted.
2. **Payment** is completed manually by the user on the bank's gateway.
3. Keep your IRCTC account credentials secure; never commit `config.py`
   to version control.
4. This tool is intended for personal use to assist with legitimate
   ticket booking only.

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| ChromeDriver version mismatch | `pip install -U webdriver-manager` |
| Elements not found | IRCTC may have updated their UI; check XPaths in modules |
| Login fails | Verify credentials; ensure no active IRCTC session elsewhere |
| OTP not received | Check registered mobile number on IRCTC account |

---

## 📝 Logging

Session logs are written to `logs/session_YYYYMMDD_HHMMSS.log`
with timestamps, log levels, and module names for easy debugging.
