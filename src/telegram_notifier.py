from src.models import Notification
from telepot import Bot  # type: ignore


class TelegramNotifier:
    """Class that sends notifications to a Telegram user."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def send_notification(self, telegramId: str, notification: Notification) -> None:
        self.bot.sendMessage(telegramId, notification.message)  # type: ignore
