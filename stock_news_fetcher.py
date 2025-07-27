import os
import json
import yfinance as yf
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# --- Configuration ---
SEEN_NEWS_FILE = "seen_news.json"

def load_seen_news(file_path: str) -> set:
    """
    Loads the set of seen news URLs from a JSON file.
    Uses a set for efficient O(1) average time complexity for lookups.
    Returns an empty set if the file doesn't exist or is invalid.
    """
    try:
        with open(file_path, 'r') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file is not found or is empty/corrupt, start with an empty set.
        return set()

def save_seen_news(file_path: str, seen_urls: set):
    """Saves the updated set of seen news URLs back to the JSON file."""
    with open(file_path, 'w') as f:
        # Convert the set to a list for JSON serialization.
        json.dump(list(seen_urls), f, indent=4)

def get_stock_tickers() -> list[str]:
    """
    Loads and parses the comma-separated stock tickers from the .env file.
    Returns an empty list if the STOCK_LIST variable is not found or is empty.
    """
    load_dotenv()
    stock_list_str = os.getenv("STOCK_LIST")
    if not stock_list_str:
        print("⚠️  Warning: 'STOCK_LIST' not found in .env file or is empty.")
        return []
    # Clean up whitespace and return a list of tickers
    return [ticker.strip() for ticker in stock_list_str.split(',')]

# --- Main Function (Refactored for Consolidated Analysis) ---
def main():
    print("📈 Fetching and analyzing stock market news...")
    
    # --- Load Config and Setup Gemini ---
    load_dotenv()
    tickers = get_stock_tickers()
    api_key = os.getenv("GEMINI_API_KEY")

    # if not api_key:
    #     print("❌ GEMINI_API_KEY not found. Cannot perform analysis.")
    #     gemini_model = None
    # else:
    #     genai.configure(api_key=api_key)
    #     gemini_model = genai.GenerativeModel('gemini-pro')

    # --- Load Seen URLs ---
    seen_urls = load_seen_news(SEEN_NEWS_FILE)
    
    # --- Step 1: Collect all new articles and group them by ticker ---
    all_new_articles_by_ticker = {}
    print("Collecting all new articles...")
    for ticker_symbol in tickers:
        try:
            news_list = yf.Ticker(ticker_symbol).news
            if not news_list: continue

            print(f"✅ Found {len(news_list)} news articles for {ticker_symbol}.")

            for article in news_list:
                
                article_url = article.get('content', {}).get('link', 'data not available')

                # print(f"Processing article: {article.get('content', {}).get('title', 'No title')}")
                # Initialize list for this ticker if it's the first new article
                if ticker_symbol not in all_new_articles_by_ticker:
                    all_new_articles_by_ticker[ticker_symbol] = []
                
                content = article.get('content', {})
                article_data = {
                    'title': content.get('title'),
                    'summary': content.get('summary')
                }
                # Add article data if it has a title
                if article_data['title']:
                    all_new_articles_by_ticker[ticker_symbol].append(article_data)
                
                seen_urls.add(article_url) # Mark URL as seen
        except Exception as e:
            print(f"❌ Could not fetch data for {ticker_symbol}: {e}")

    # --- Step 2: Analyze each ticker's collected news ---
    if not all_new_articles_by_ticker:
        print("\n✅ No new articles found to analyze.")
        return

    print(f"\nFound new articles for {len(all_new_articles_by_ticker)} ticker(s). Analyzing...")
    print(all_new_articles_by_ticker)
    
    # for ticker, news_items in all_new_articles_by_ticker.items():
    #     analysis = None
    #     if gemini_model:
    #         print(f"🧠 Analyzing {len(news_items)} news item(s) for {ticker}...")
    #         analysis = analyze_stock_with_gemini(gemini_model, ticker, news_items)
    #         time.sleep(1) # Respect API rate limits

    #     # --- Display the consolidated analysis for the stock ---
    #     print("=" * 60)
    #     print(f"📈 Consolidated Analysis for: {ticker}")
    #     print("=" * 60)

    #     if analysis:
    #         print(f"  Overall Sentiment: {analysis.get('overall_sentiment', 'N/A')}")
    #         print(f"  Overall Impact:    {analysis.get('overall_impact_score', 'N/A')}/10")
    #         print(f"\n  Key Drivers: {analysis.get('key_drivers', 'N/A')}")
            
    #         most_impactful = analysis.get('most_impactful_news', {})
    #         print(f"\n  Most Impactful News Title: {most_impactful.get('title', 'N/A')}")
    #         print(f"  Reasoning: {most_impactful.get('reasoning', 'N/A')}")
    #     else:
    #         print("--- AI Analysis could not be performed ---")
    #     print("=" * 60 + "\n")

    # # --- Step 3: Save the updated list of seen URLs ---
    # save_seen_news(SEEN_NEWS_FILE, seen_urls)
    # print(f"✅ Process complete. Saved {len(seen_urls)} total URLs to {SEEN_NEWS_FILE}.")


if __name__ == "__main__":
    main()