from dotenv import load_dotenv
from typing import Dict, Any, List
import yfinance as yf
load_dotenv() 


def get_stock_data(ticker: str) -> Dict[str, Any]:
    """Fetches stock data for a
      given stock ticker using yfinance.
    
    Args:
        ticker (str): The stock ticker
      symbol (e.g., "AAPL", "MSFT").
    
    Returns:
        Dict[str, Any]: A dictionary
      containing selected stock information,
      or an error message if the ticker is invalid.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return {"error": f"Could not retrieve data for ticker: {ticker}. It might be invalid."}

        # Extract relevant information
        data = {
            "ticker": ticker,
            "shortName": info.get("shortName", "N/A"),
            "currentPrice": info.get("currentPrice", "N/A"),
            "previousClose": info.get("previousClose", "N/A"),
            "open": info.get("open", "N/A"),
            "dayHigh": info.get("dayHigh", "N/A"),
            "dayLow": info.get("dayLow", "N/A"),
            "volume": info.get("volume", "N/A"),
            "marketCap": info.get("marketCap", "N/A"),
            "currency": info.get("currency", "N/A"),
            "exchange": info.get("exchange", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "longBusinessSummary": info.get("longBusinessSummary", "N/A")
        }
        return data
    except Exception as e:
        return {"error": f"An unexpected error occurred while fetching data for {ticker}: {e}"}


def get_financial_data(ticker: str) -> str:
    """Fetches stock data for a
      given stock ticker using yfinance.
    
    Args:
        ticker (str): The stock ticker
      symbol (e.g., "AAPL", "MSFT").
    
    Returns:
        str: A String of data containing income_statement, 
        cash_flow, balance_sheet, financials, historical_month_data
      or an error message if the ticker is invalid.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info:
            return {"error": f"Could not retrieve data for ticker: {ticker}. It might be invalid."}

        # Extract relevant information
        data = f"""
            'income_statement': 
            {stock.income_stmt}

            'cash_flow': 
            {stock.cash_flow}

            'balance_sheet': 
            {stock.balance_sheet}

            'financials': 
            {stock.financials}

            'historical_month_data':
            {stock.history(period='1mo')}
        """
        return data
    except Exception as e:
        return {"error": f"An unexpected error occurred while fetching data for {ticker}: {e}"}



def get_news_articles(query: str) -> List[Dict]:
    """Fetch news articles based on query or ticker symbol.
    
    Args:
        query: Search keywords or phrases (str)
            
    Returns:
        List of news articles with title, description, url, etc.
    """
    try:
        from newsapi import NewsApiClient
        import os
        
        newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        response = newsapi.get_everything(
            q=query,
            language="en",
            sort_by="publishedAt",
            page_size=10
        )
        return response.get("articles", [])
    except Exception as e:
        return {"error": f"Failed to fetch news: {str(e)}"}