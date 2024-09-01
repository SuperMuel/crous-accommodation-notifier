import logging
from time import sleep
from typing import List, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver

from src.models import Accommodation, SearchResults, SearchUrl
from src.settings import Settings

settings = Settings()

logger = logging.getLogger(__name__)


class Authenticator:
    """Class that handles the authentication to the CROUS website and returns a WebDriver object that is authenticated."""

    def __init__(self, email: str, password: str, delay: int = 2):
        self.email = email
        self.password = password
        self.delay = delay

    def authenticate_driver(self, driver: WebDriver) -> None:
        """Authenticates the given WebDriver object to the CROUS website."""

        logger.info("Authenticating to the CROUS website...")

        sleep(self.delay)

        # Step 1: Go to the login page

        logger.info(f"Going to the login page: {settings.MSE_LOGIN_URL}")
        driver.get(settings.MSE_LOGIN_URL)
        sleep(self.delay)

        # Step 2: choose the correct authentication method
        logger.info("Choosing the correct authentication method")
        mse_connect_button = driver.find_element(By.CLASS_NAME, "loginapp-button")
        # mse_connect_button.click() # somehow doesn't work. We simulate a click instead :
        driver.execute_script("arguments[0].click();", mse_connect_button)
        sleep(self.delay)

        # Step 3: Input credentials and submit
        logger.info("Inputting credentials")
        username_input = driver.find_element(By.NAME, "j_username")
        password_input = driver.find_element(By.NAME, "j_password")

        username_input.send_keys(self.email)
        password_input.send_keys(self.password)

        logger.info("Submitting the form")
        password_input.send_keys(Keys.RETURN)

        sleep(self.delay)

        # Step 4: Validate the rules
        self._validate_rules(driver)

        logger.info("Successfully authenticated to the CROUS website")

    def _validate_rules(self, driver: WebDriver) -> None:
        """Validates the rules of the CROUS website."""
        logger.info("Validating the rules of the CROUS website")

        driver.get("https://trouverunlogement.lescrous.fr/tools/36/rules")

        sleep(self.delay)

        # <button class="fr-btn" type="submit" name="searchSubmit">Passer à la recherche de logements</button>

        validate_button = driver.find_element(By.NAME, "searchSubmit")

        validate_button.click()

        sleep(self.delay)


class Parser:
    """Class to parse the CROUS website and get the available accommodations"""

    def __init__(self, authenticated_driver: WebDriver):
        self.driver = authenticated_driver

    def get_accommodations(self, search_url: SearchUrl) -> SearchResults:
        """Returns the accommodations found on the CROUS website for the given search URL"""
        logger.info(f"Getting accommodations from the search URL: {search_url}")
        self.driver.get(search_url)
        sleep(2)
        html = self.driver.page_source
        search_results_soup = BeautifulSoup(html, "html.parser")
        num_accommodations = self._get_accomodations_count(search_results_soup)
        logger.info(f"Found {num_accommodations} accommodations")

        return SearchResults(
            search_url=search_url,
            count=num_accommodations,
            accommodations=self._parse_accommodations_summaries(search_results_soup),
        )

    def _get_accomodations_count(
        self, search_results_soup: BeautifulSoup
    ) -> Optional[int]:
        results_heading = search_results_soup.find(
            "h2", class_="SearchResults-desktop fr-h4 svelte-11sc5my"
        )

        if not results_heading:
            return None

        number_or_aucun = results_heading.text.split()[0]

        if number_or_aucun == "Aucun":
            return 0

        try:
            number = int(number_or_aucun)
            return number
        except ValueError:
            return None

    def _parse_accommodations_summaries(
        self, search_results_soup: BeautifulSoup
    ) -> List[Accommodation]:
        # TODO : This only gets the first page of results. We need to get all the pages.

        cards = search_results_soup.find_all("div", class_="fr-card")

        accommodations: List[Accommodation] = []
        for card in cards:
            title_card = card.find("h3", class_="fr-card__title")
            if not title_card:
                continue
            title = title_card.text.strip()

            # TODO: find the id

            accommodations.append(Accommodation(title=title, id=None))

        return accommodations
