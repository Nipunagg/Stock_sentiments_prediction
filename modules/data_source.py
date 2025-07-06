"""
Data source module for the Stock News Predictor.
This module handles loading tickers and fetching news.
"""
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import TICKERS_FILE, NEWS_SOURCE, NEWS_ITEMS_LIMIT,ALPHA_VANTAGE_APT_KEY
import requests

class TickerLoader:
    """Class for loading tickers from a Google Sheet or a local CSV file."""

    def __init__(self, sheet_id=None, credentials_file=None, csv_file=None):
        """Initialize the ticker loader."""
        self.sheet_id = sheet_id
        self.credentials_file = credentials_file
        self.csv_file = csv_file
        self.client = None
        self.sheet = None

    def authenticate(self):
        """Authenticate with Google Sheets API."""
        if not self.credentials_file:
            raise ValueError("Credentials file is required for Google Sheets access.")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(self.sheet_id).sheet1

    def load_tickers(self):
        """Load tickers from a Google Sheet or a local CSV file."""
        if self.csv_file:
            return self._load_from_csv()
        elif self.sheet_id and self.credentials_file:
            if not self.sheet:
                self.authenticate()
            return self._load_from_google_sheet()
        else:
            raise ValueError("Either csv_file or sheet_id and credentials_file must be provided.")

    def _load_from_google_sheet(self):
        """Load tickers from a Google Sheet."""
        # Get all records from the sheet
        records = self.sheet.get_all_records()
        if not records:
            print("No records found in the Google Sheet.")
            return []

        # Extract ticker symbols from the records
        tickers = [record.get("Ticker") for record in records if record.get("Ticker")]
        return tickers

    def _load_from_csv(self):
        """Load tickers from a local CSV file."""
        if not self.csv_file:
            raise ValueError("CSV file path is required for loading from CSV.")
        df = pd.read_csv(self.csv_file)
        if 'Ticker' not in df.columns:
            raise ValueError("CSV file must contain a 'Ticker' column.")
        return df['Ticker'].tolist()

class NewsFetcher:
    """Class for fetching news from various sources."""

    def __init__(self, news_source=NEWS_SOURCE, items_limit=NEWS_ITEMS_LIMIT):
        """Initialize the news fetcher."""
        self.news_source = news_source
        self.items_limit = items_limit

    def fetch_news(self, ticker):
        """Fetch news for a specific ticker."""
        if self.news_source == "yahoo_finance":
            return self._fetch_from_yahoo_finance(ticker)
        elif self.news_source == "alpha_vantage":
            return self._fetch_from_alpha_vantage(ticker)
        elif self.news_source == "newsapi":
            return self._fetch_from_newsapi(ticker)
        else:
            print(f"Unsupported news source: {self.news_source}. Skipping ticker: {ticker}")
            return []

    def _fetch_from_yahoo_finance(self, ticker):
        """Fetch news from Yahoo Finance."""
        import yfinance as yf
        stock = yf.Ticker(ticker)
        news = stock.news
        return news

    def _fetch_from_alpha_vantage(self, ticker):
        """Fetch news from Alpha Vantage."""
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&limit=1&apikey={ALPHA_VANTAGE_APT_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "feed" in data:
                news_items = []
                for item in data["feed"]:
                    news_item = {
                        "title": item.get("title", ""),
                        "link": item.get("url", ""),
                        "summary": item.get("summary", ""),
                        "impact_score": item.get("overall_sentiment_score", 0),
                        "ticker": ticker
                    }
                    print(news_item["summary"])
                    news_items.append(news_item)
                    break
                return news_items
            else:
                print(f"No news found for ticker: {ticker}")
                return []
        else:
            print(f"Error fetching news from Alpha Vantage: {response.status_code} - {response.text}")
            return []

    def _fetch_from_newsapi(self, ticker):
        """Fetch news from NewsAPI."""
        # Implement NewsAPI news fetching
        pass

    def fetch_all_new_news(self, tickers):
        """Fetch all new news for a list of tickers."""
        all_news = []
        for ticker in tickers:
            news = self.fetch_news(ticker)
            all_news.extend(news)
        return all_news
