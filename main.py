import argparse
import logging
import os
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
import telepot
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from accommodation_parser import Authenticator, Parser
from models import UserConf
from notification_builder import NotificationBuilder
from telegram_notifier import TelegramNotifier


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
logger = logging.getLogger("accommodation_notifier")


def check_environment_variables_exist() -> None:
    error = False
    for var in ["MSE-EMAIL", "MSE-PASSWORD", "TELEGRAM_BOT_TOKEN"]:
        if not os.environ.get(var):
            logger.error(f"ERROR : Missing environment variable {var}")
            error = True
    if error:
        raise RuntimeError("Missing environment variables")
    logger.info("All environement variables found.")


def load_users_conf() -> List[UserConf]:
    return [
        UserConf(
            "Me",
            "My telegram ID",
            "https://trouverunlogement.lescrous.fr/tools/32/search?bounds=4.863204361956362_45.791317414424945_4.8871940393855615_45.76566686734247",
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
        options=chrome_options, service=ChromeService(ChromeDriverManager().install())
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

    load_dotenv()
    check_environment_variables_exist()
    EMAIL = os.environ["MSE-EMAIL"]
    PASSWORD = os.environ["MSE-PASSWORD"]

    bot = telepot.Bot(os.environ["TELEGRAM_BOT_TOKEN"])
    user_confs = load_users_conf()

    driver = create_driver(headless=not args.no_headless)
    Authenticator(EMAIL, PASSWORD).authenticate_driver(driver)

    parser = Parser(driver)
    notification_builder = NotificationBuilder()
    notifier = TelegramNotifier(bot)

    for conf in user_confs:
        logging.info(f"Handling configuration : {conf}")
        search_results = parser.get_accommodations(conf.search_url)
        notification = notification_builder.search_results_notification(search_results)
        notifier.send_notification(conf.telegram_id, notification)

    driver.quit()
