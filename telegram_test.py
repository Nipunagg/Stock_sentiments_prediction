import asyncio
import telebot
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramNotifier:
    """Class for sending notifications to Telegram."""

    def __init__(self, bot_token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        """Initialize the Telegram notifier."""
        bot_token="8189619359:AAECWdP56uNmziu16TKzsmFosKb4nU5ttn8"
        self.bot = telebot.TeleBot(bot_token)
        self.chat_id = chat_id

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
	        self.bot.reply_to(message, "Howdy, how are you doing?")


    
        @self.bot.message_handler()
        def notify_news(self, query):
            """Send a notification for a news item."""
            try:
                message = {"Hello" :query}
                self.bot.send_message(self.chat_id, message)
                print(f"Notification sent for news item:")
            except Exception as e:
                print(f"Error sending notification: {e}")

        self.bot.infinity_polling()

notify = TelegramNotifier()
notify.notify_news("Hi")
