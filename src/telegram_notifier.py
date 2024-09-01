from src.models import Notification
from telepot import Bot  # type: ignore


class TelegramNotifier:
    """Class that sends notifications to a Telegram user."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def send_notification(
        self, telegramId: str, notification: Notification, parse_mode: str = "Markdown"
    ) -> None:
        self.bot.sendMessage(telegramId, notification.message, parse_mode=parse_mode)  # type: ignore
