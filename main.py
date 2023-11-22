import logging
import os
import time
from json import loads
from time import sleep
import selenium

import telepot
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver


logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
)
logger = logging.getLogger("accommodation_notifier")

DEFAULT_SLEEPING_TIME_SEC = 600
EXAMPLE_SEARCH_URL = "https://trouverunlogement.lescrous.fr/tools/31/search?bounds=1.6367308693924134_49.43777096183293_3.1720702248611636_47.9329065912321"
LOGIN_URL = (
    "https://www.messervices.etudiant.gouv.fr/envole/oauth2/login?redirect=/tul/"
)


# Fonction pour compter les logements disponibles
def get_accomodations_count(soup) -> int:
    results_heading = soup.find(
        "h2", class_="SearchResults-desktop fr-h4 svelte-11sc5my"
    )

    if results_heading:
        number_or_aucun = results_heading.text.split()[0]
        if number_or_aucun == "Aucun":
            return 0
        else:
            try:
                number = int(number_or_aucun)
                return number
            except ValueError:
                raise ValueError(f"Could not parse heading : {results_heading.text}")
    else:
        raise ValueError(f"No heading found : {results_heading=}")


def get_logement_summaries(soup) -> list[str]:
    cards = soup.find_all("div", class_="fr-card")

    summaries = []
    for card in cards:
        description = card.find("h3", class_="fr-card__title").text.strip()
        details = card.find(class_="fr-card__end")
        if details:
            details = (
                details.text.strip().strip("(").strip(")").replace(", ", "\n     - ")
            )
            description += f"\n     - ({details})"
        summaries.append(description)

    return summaries


def create_accommodations_notification(num_accommodations, summaries, url) -> str:
    assert num_accommodations >= 1

    verb = "est" if num_accommodations == 1 else "sont"
    s = "s" if num_accommodations > 1 else ""

    msg = (
        f"Bonne nouvelle 😯, {num_accommodations} logement{s} {verb} disponible{s} : \n "
    )
    for summary in summaries:
        msg += f"\t- {summary}\n"

    missing_logements_summaries = num_accommodations - len(summaries)
    if missing_logements_summaries > 0:
        s = "s" if missing_logements_summaries > 1 else ""
        msg += f"+ {missing_logements_summaries} logement{s}.\nRdv sur {url} pour consulter la totalité des résultats\n"

    return msg


def get_authenticated_driver(email, password, delay=5, headless=True) -> WebDriver:
    # Set up Chrome options for headless mode
    chrome_options = Options()
    if os.environ.get("GOOGLE_CHROME_BIN"):
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    if headless:
        chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")

    # Initialize the WebDriver with the configured options
    driver = webdriver.Chrome(options=chrome_options)

    # sleep(delay)

    driver.get(LOGIN_URL)

    # choose the correct authentication method
    mse_connect_button = driver.find_element(By.CLASS_NAME, "loginapp-button")
    # mse_connect_button.click() # somehow doesn't work. We simulate a click instead :
    driver.execute_script("arguments[0].click();", mse_connect_button)

    sleep(delay)

    # Step 3: Input credentials and submit
    username_input = driver.find_element(By.NAME, "j_username")
    password_input = driver.find_element(By.NAME, "j_password")

    username_input.send_keys(email)
    password_input.send_keys(password)

    password_input.send_keys(
        Keys.RETURN
    )  # Alternatively, can find and click the submit button

    sleep(delay)

    # Skip the explanation

    driver.get(EXAMPLE_SEARCH_URL)

    try:
        continue_button = driver.find_element(By.NAME, "searchSubmit")
        continue_button.click()
        sleep(delay)
    except NoSuchElementException as e:
        logger.debug(
            f"Could not find the 'Passer à la recherche des logements' button. Ignoring it.\n{e}"
        )

    return driver


def check_environment_variables_exist() -> None:
    # Check optional variables :
    if not os.environ.get("CROUS-ACCOMMODATION-NOTIFIER-DELAY-SEC"):
        logger.info(
            f'Environment variable "CROUS-ACCOMMODATION-NOTIFIER-DELAY" not found. Default value of {DEFAULT_SLEEPING_TIME_SEC} seconds will be used.'
        )

    # Check mandatory variables :
    error = False
    for var in ["MSE-EMAIL", "MSE-PASSWORD", "TELEGRAM_BOT_TOKEN"]:
        if not os.environ.get(var):
            logger.error(f"ERROR : Missing environment variable {var}")
            error = True
    if error:
        raise RuntimeError("Missing environment variables")
    logger.info("All environement variables exist.")


def notify_users_of_exit(users, bot) -> None:
    for user in users:
        username = user["username"]
        telegramId = user["telegramId"]
        url = user["url"]

        bot.sendMessage(
            telegramId,
            f"Désolé, je dois m'absenter un moment. Durant cette période, je ne vous préviendrai pas si un logement est à nouveau disponible. Je vous préviendrai dès mon retour.",
        )
        logger.info(f"\t Notified {username} about the interruption")

    logger.info("Notified everyone.")


def load_users_conf():
    """
    Loads the users configuration from USERS_JSON environment variable if it exists, otherwise from users.json file.
    """
    if os.environ.get("USERS_JSON"):
        users = loads(os.environ.get("USERS_JSON"))
        logger.info("Users configuration loaded from USERS_JSON environment variable.")
    else:
        users = loads(open("users.json", "r").read())
        logger.info("Users configuration loaded from users.json file.")
    return users


if __name__ == "__main__":
    load_dotenv()
    check_environment_variables_exist()
    EMAIL = os.environ["MSE-EMAIL"]
    PASSWORD = os.environ["MSE-PASSWORD"]
    SLEEPING_TIME_SEC = int(
        os.environ.get(
            "CROUS-ACCOMMODATION-NOTIFIER-DELAY-SEC", DEFAULT_SLEEPING_TIME_SEC
        )
    )

    bot = telepot.Bot(os.environ["TELEGRAM_BOT_TOKEN"])

    users = load_users_conf()

    # Initialisation :

    logger.info("CROUS-ACCOMMODATION-NOTIFIER is starting...")

    logger.info(
        f"Creating a Selenium driver and authentication using account {EMAIL[:5]}..."
    )
    driver = get_authenticated_driver(EMAIL, PASSWORD, delay=5, headless=True)
    logger.info("Successfully got an authenticated driver.")

    logger.info("Starting with notifying users that the bot started.")

    for config in users:
        username = config["username"]
        telegramId = config["telegramId"]
        url = config["url"]

        bot.sendMessage(
            telegramId,
            f"Bonjour {username}. J'ai démarré la surveillance de l'url suivante : \n\n{url}.\n\n Vous serez alerté(e) dès qu'un logement sera disponible.",
        )
        logger.info(f"\tNotified {username}.")

    logger.info("Notified everyone about the start.")

    logger.info(f"Starting handling {len(users)} configuration(s).")

    # Keeps the last notification sent to each user.
    notifications_dict = dict()  # userId->notification

    try:
        while True:
            for config in users:
                username = config["username"]
                telegramId = config["telegramId"]
                url = config["url"]

                logger.info(f'\tHandling "{username}" configuration.')

                try:
                    driver.get(url)
                    time.sleep(2)
                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    num_accommodations = get_accomodations_count(soup)
                except Exception as e:
                    logger.exception(
                        f"\t\tError while searching for accommodations. \n{config=}\n\n {type(e).__name__} {e}"
                    )  # TODO : redirect logging.error to my telegram
                    continue

                logger.info(
                    f"\t\t'{username}' has {num_accommodations} available accommodations."
                )

                if num_accommodations > 0:
                    accommodations_summaries = get_logement_summaries(soup)

                    notification = create_accommodations_notification(
                        num_accommodations, accommodations_summaries, url
                    )
                else:
                    notification = "Aucun logement trouvé. Voici une liste des ponts de France où vous pourriez dormir : https://fr.wikipedia.org/wiki/Liste_de_ponts_de_France"

                if notifications_dict.get(telegramId) == notification:
                    logger.info("\t\t Already sent the same notification.")
                else:
                    bot.sendMessage(telegramId, notification)
                    logger.info("\t\tSent notification.")
                notifications_dict[telegramId] = notification

            logger.info(
                f"Sleeping {SLEEPING_TIME_SEC} seconds ({SLEEPING_TIME_SEC/60:.1f} minutes)"
            )
            time.sleep(SLEEPING_TIME_SEC)

    except Exception as e:
        logger.error("Unknown error", e)
        notify_users_of_exit(users, bot)
        logger.critical("Exiting")
    except KeyboardInterrupt:
        logger.critical("KeyboardInterrupt.")
        notify_users_of_exit(users, bot)
        logger.critical("Exiting")
    finally:
        driver.quit()
