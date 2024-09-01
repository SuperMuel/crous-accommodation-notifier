import logging
from time import sleep
from typing import List, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver

from src.models import Accommodation, SearchResults, SearchUrl
from src.settings import Settings

settings = Settings()

logger = logging.getLogger(__name__)


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
