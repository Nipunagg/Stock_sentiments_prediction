"""
Analysis module for the Stock News Predictor.
This module handles analyzing news using an AI model via API.
"""
import requests
from config.settings import OPENAI_API_KEY, GROQ_API_KEY, USE_GROQ

class NewsAnalyzer:
    """Class for analyzing news using an AI model via API."""

    def __init__(self, api_key=GROQ_API_KEY, use_groq=True):
        """Initialize the news analyzer."""
        self.api_key = api_key
        self.use_groq = use_groq

    def analyze_news(self, news_item):
        """Analyze a news item using an AI model via API."""
        if self.use_groq:
            return self._analyze_with_groq(news_item)
        #else:
            #return self._analyze_with_openai(news_item)

    def _analyze_with_openai(self, news_item):
        """Analyze news using OpenAI API."""
        url = "https://api.openai.com/v1/engines/davinci-codex/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "prompt": f"Analyze the following news item and provide an impact score (1-5) and a summary:\n\n{news_item}",
            "max_tokens": 150,
            "temperature": 0.7,
            "n": 1,
            "stop": None
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["text"].strip()
        else:
            raise Exception(f"Error analyzing news with OpenAI: {response.status_code} - {response.text}")

    def _analyze_with_groq(self, news_item):
        """Analyze news using Groq API."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{
                "role": "system",
                    "content": "You are a stock analyst.YOu have given a summary you need to rate the sentiment between 1 to5 "},{
                        "role": "user",
                        "content": news_item["summary"]
                    }]
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            print(result)
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Error analyzing news with Groq: {response.status_code} - {response.text}")
