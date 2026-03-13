import logging
import os
# import winsound
import smtplib
import time
from email.message import EmailMessage

import requests
from dotenv import load_dotenv

# 1. Setup Logging
# This creates a file that records every check. 'a' means it appends (doesn't overwrite).
logging.basicConfig(
    filename='wissel_check.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 2. Load environment variables
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
AMAZON_LINK = os.getenv("AMAZON_LINK")

SLEEP_TIME = 10


def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        logging.info("Email notification sent successfully!")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")


def main():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    logging.info("--- Monitor Started (Background Mode) ---")
    already_notified = False

    while True:
        try:
            response = session.get(AMAZON_LINK, timeout=15)

            if "Dit merk is tijdelijk uitverkocht!" not in response.text:
                if not already_notified:
                    logging.info("MATCH FOUND: Amazon cards are in stock!")
                    # winsound.Beep(2500, 1000)
                    send_email("Amazon Cards in Stock!", f"Available now at: {AMAZON_LINK}")
                    already_notified = True
            else:
                # We log this at "DEBUG" or just skip it to keep the file small,
                # but for now, let's log one "still running" message every hour.
                if time.localtime().tm_min == 0 and time.localtime().tm_sec < SLEEP_TIME:
                    logging.info("Hourly Status: Script is running. Still out of stock.")

                already_notified = False

        except requests.exceptions.RequestException as e:
            # This catches that 'getaddrinfo failed' error and logs it
            logging.warning(f"Network issue: {e}. Retrying in 30s...")
            time.sleep(30)
            continue

        time.sleep(SLEEP_TIME)  # 10 seconds is very safe for long-term background running


if __name__ == "__main__":
    main()
