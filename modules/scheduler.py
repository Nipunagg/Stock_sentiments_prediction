"""
Scheduler module for the Stock News Predictor.
This module handles periodic execution of the news checking process.
"""
import asyncio
import threading
import schedule
from datetime import datetime
from config.settings import CHECK_INTERVAL_MINUTES, TICKERS_FILE, NEWS_SOURCE, NEWS_ITEMS_LIMIT
from modules.data_source import TickerLoader, NewsFetcher
from modules.analysis import NewsAnalyzer
from modules.notification import TelegramNotifier

class NewsScheduler:
    """Class for scheduling periodic news checks."""

    def __init__(self, sheet_id=None, credentials_file=None, csv_file=None):
        """Initialize the news scheduler."""
        self.ticker_loader = TickerLoader(sheet_id=sheet_id, credentials_file=credentials_file, csv_file=csv_file)
        self.news_fetcher = NewsFetcher(news_source=NEWS_SOURCE, items_limit=NEWS_ITEMS_LIMIT)
        self.news_analyzer = NewsAnalyzer()
        self.notifier = TelegramNotifier()
        self.running = False
        self.scheduler_thread = None

    async def check_news(self):
        """Check for news and send notifications."""
        print(f"Checking news at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
        try:
            # Load tickers
            tickers = self.ticker_loader.load_tickers()
            if not tickers:
                print("No tickers found. Please check the tickers file.")
                return
            print(f"Loaded {len(tickers)} tickers.")

            # Fetch new news
            news_items = self.news_fetcher.fetch_all_new_news(tickers)
            if not news_items:
                print("No new news found.")
                return

            print(f"Found {len(news_items)} new news items.")

            # Analyze and notify
            for news_item in news_items:
                try:
                    # Analyze the news
                    analyzed_news = await self.news_analyzer.analyze_news(news_item)
                    # Send notification
                    await self.notifier.notify_news(analyzed_news)
                except Exception as e:
                    print(f"Error processing news item: {e}")
        except Exception as e:
            print(f"Error checking news: {e}")

    async def run_scheduler(self):
        """Run the scheduler in a loop."""
        schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(self.check_news)
        while self.running:
            schedule.run_pending()
            await asyncio.sleep(1)

    def start(self):
        """Start the scheduler."""
        if self.running:
            print("Scheduler is already running.")
            return

        self.running = True
        # Run once immediately
        asyncio.run(self.check_news())
        # Start the scheduler thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        print(f"Scheduler started. Checking news every {CHECK_INTERVAL_MINUTES} minutes.")

    def _run_scheduler_loop(self):
        """Run the scheduler in a loop."""
        asyncio.run(self.run_scheduler())

    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            print("Scheduler is not running.")
            return

        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("Scheduler stopped.")
