from models import Notification, SearchResults


class NotificationBuilder:
    """Class that builds notifications from search results."""

    def search_results_notification(
        self, search_results: SearchResults
    ) -> Notification:
        accommodations = search_results.accommodations
        if not accommodations:
            message = "Aucun logement trouvé. Voici une liste des ponts de France où vous pourriez dormir : https://fr.wikipedia.org/wiki/Liste_de_ponts_de_France"
        else:
            s = "s" if len(accommodations) > 1 else ""
            verb = "sont" if len(accommodations) > 1 else "est"
            message = f"Bonne nouvelle 😯, {len(accommodations)} logement{s} {verb} disponible{s} : \n "

        for accommodation in accommodations:
            message += f"\n - {accommodation.title}"

        message += f"\n\n{search_results.search_url}"

        return Notification(message)
