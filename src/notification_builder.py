from src.models import Accommodation, Notification, SearchResults


class NotificationBuilder:
    """Class that builds notifications from search results."""

    def __init__(self, notify_when_no_results: bool = False):
        self.notify_when_no_results = notify_when_no_results

    def search_results_notification(
        self, search_results: SearchResults
    ) -> Notification | None:
        accommodations = search_results.accommodations
        if not accommodations and not self.notify_when_no_results:
            return None

        if not accommodations:
            message = "Aucun logement trouvé. Voici une liste des ponts de France où vous pourriez dormir : https://fr.wikipedia.org/wiki/Liste_de_ponts_de_France"
        else:
            s = "s" if len(accommodations) > 1 else ""
            verb = "sont" if len(accommodations) > 1 else "est"
            message = f"Bonne nouvelle 😯, {len(accommodations)} logement{s} {verb} disponible{s} : \n "

        def format_one_accommodation(accommodation: Accommodation):
            price = (
                f"{accommodation.price}€"
                if isinstance(accommodation.price, float)
                else accommodation.price
            )

            link = f"https://trouverunlogement.lescrous.fr/tools/36/accommodations/{accommodation.id}"

            return f"[*{accommodation.title}*]({link}) ({price})"

        message += "\n\n".join(map(format_one_accommodation, accommodations))

        message += f"\n\n{search_results.search_url}"

        return Notification(message=message)
