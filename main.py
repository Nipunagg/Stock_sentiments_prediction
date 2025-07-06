import os
import sys
import argparse
import asyncio
from modules.data_source import TickerLoader, NewsFetcher
from modules.analysis import NewsAnalyzer
from modules.notification import TelegramNotifier
from modules.scheduler import NewsScheduler

def ensure_cache_directory():
    """Ensure the cache directory exists."""
    os.makedirs("data", exist_ok=True)

    # Create an empty cache file if it doesn't exist
    if not os.path.exists("data/news_cache_json"):
        with open("data/news_cache_json", "w") as f:
            f.write("{}")

async def run_once(sheet_id=None, credentials_file=None, csv_file=None):
    """Run the news check once and exit."""
    print("Running news check once...")
    scheduler = NewsScheduler(sheet_id=sheet_id, credentials_file=credentials_file, csv_file=csv_file)
    await scheduler.check_news()
    print("News check completed.")

async def run_scheduler(sheet_id=None, credentials_file=None, csv_file=None):
    """Run the scheduler continuously."""
    print("Starting scheduler...")
    scheduler = NewsScheduler(sheet_id=sheet_id, credentials_file=credentials_file, csv_file=csv_file)
    scheduler.start()
    try:
        # Keep the main thread alive
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nstopping scheduler...")
        scheduler.stop()
        print("scheduler stopped.")

async def main():
    """main function"""
    parser = argparse.ArgumentParser(description="Stock News Predictor")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run the news check once and exit")
    parser.add_argument(
        "--sheet_id",
        type=str,
        help="Google Sheet ID for ticker symbols")
    parser.add_argument(
        "--credentials_file",
        type=str,
        help="Path to Google Sheets API credentials file")
    parser.add_argument(
        "--csv_file",
        type=str,
        help="Path to the local CSV file containing ticker symbols")
    args = parser.parse_args()
    ensure_cache_directory()
    if args.once:
        await run_once(args.sheet_id, args.credentials_file, args.csv_file)
    else:
        await run_scheduler(args.sheet_id, args.credentials_file, args.csv_file)

if __name__ == "__main__":
    asyncio.run(main())
