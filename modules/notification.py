"""
Notification module for the Stock News Predictor.
This module handles sending notifications to Telegram.
"""
import telebot
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    """Class for sending notifications to Telegram."""

    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        """Initialize the Telegram notifier."""
        self.bot = telebot.TeleBot(bot_token)
        self.chat_id = chat_id

    async def notify_news(self, news_item):
        """Send a notification for a news item."""
        try:
            message = self._format_message(news_item)
            self.bot.send_message(self.chat_id, message)
            print(f"Notification sent for news item: {news_item['title']}")
        except Exception as e:
            print(f"Error sending notification: {e}")

    def _format_message(self, news_item):
        """Format a news item as a message."""
        ticker = news_item.get("ticker", "N/A")
        summary = news_item.get("summary", "No summary available.")
        link = news_item.get("link", "#")
        impact_score = news_item.get("impact_score", "N/A")

        message = (
            f"📰 New news for {ticker}:\n\n"
            f"Summary: {summary}\n\n"
            f"Read more: {link}\n\n"
            f"Impact score: {impact_score}/5"
        )
        return message
