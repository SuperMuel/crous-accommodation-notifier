import argparse
import logging
from typing import List

import telepot
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.chrome.webdriver import WebDriver
from chromedriver_py import binary_path  # this will get you the path variable

from accommodation_parser import Authenticator, Parser
from models import UserConf
from notification_builder import NotificationBuilder
from settings import Settings
from telegram_notifier import TelegramNotifier

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
logger = logging.getLogger("accommodation_notifier")


def load_users_conf() -> List[UserConf]:
    return [
        UserConf(
            "Me",
            settings.MY_TELEGRAM_ID,
            "https://trouverunlogement.lescrous.fr/tools/36/search?bounds=4.861955965058465_45.794100252988855_4.8859456424876635_45.76704397585394",
        )
    ]


def create_driver(headless: bool = True) -> WebDriver:
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        logging.info("Running in headless mode")
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
    else:
        logging.info("Running in non-headless mode")

    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    # Initialize the WebDriver with the configured options
    return webdriver.Chrome(
        options=chrome_options,
        service=ChromiumService(
            executable_path=binary_path,
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the script in headless mode or not."
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run the script without headless mode",
    )

    args = parser.parse_args()

    settings = Settings()
    bot = telepot.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.getMe()  # test if the bot is working

    user_confs = load_users_conf()

    driver = create_driver(headless=not args.no_headless)
    Authenticator(settings.MSE_EMAIL, settings.MSE_PASSWORD).authenticate_driver(driver)

    parser = Parser(driver)
    notification_builder = NotificationBuilder()
    notifier = TelegramNotifier(bot)

    for conf in user_confs:
        logging.info(f"Handling configuration : {conf}")
        search_results = parser.get_accommodations(conf.search_url)
        notification = notification_builder.search_results_notification(search_results)
        notifier.send_notification(conf.telegram_id, notification)

    driver.quit()
