import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StockService:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.top_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']
        self.market_indices = {
            '^GSPC': 'S&P 500',
            '^DJI': 'DOW',
            '^IXIC': 'NASDAQ',
            '^RUT': 'Russell 2000',
            '^NDX': 'NASDAQ-100'  # Adding NASDAQ-100 index
        }
    
    def get_stock_data(self, ticker: str) -> Dict[str, Any]:
        """
        Get stock data for a given ticker using yfinance
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get historical data for 1 year
            hist = stock.history(period="1y")
            
            # Calculate 52-week high/low
            week52_high = hist['High'].max()
            week52_low = hist['Low'].min()
            
            # Get current price and change
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', 0)
            change = round(current_price - previous_close, 2)
            change_percent = round((change / previous_close) * 100, 2) if previous_close else 0
            
            return {
                'symbol': ticker,
                'name': info.get('shortName', ticker),
                'exchange': info.get('exchange', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'ceo': info.get('ceo', 'N/A'),
                'employees': info.get('fullTimeEmployees', 0),
                'city': info.get('city', 'N/A'),
                'country': info.get('country', 'N/A'),
                'founded': info.get('founded', 0),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', ''),
                'price': round(current_price, 2),
                'change': change,
                'change_percent': change_percent,
                'market_cap': round(info.get('marketCap', 0) / 1_000_000_000, 2),  # In billions
                'pe_ratio': round(info.get('trailingPE', 0), 2),
                'eps': round(info.get('trailingEps', 0), 2),
                'dividend_yield': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 0,
                'week52_high': round(week52_high, 2),
                'week52_low': round(week52_low, 2),
                'avg_volume': info.get('averageVolume', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'revenue_ttm': round(info.get('totalRevenue', 0) / 1_000_000_000, 2) if info.get('totalRevenue') else 0,
                'gross_profit': round(info.get('grossProfits', 0) / 1_000_000_000, 2) if info.get('grossProfits') else 0,
                'profit_margin': round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else 0,
                'return_on_equity': round(info.get('returnOnEquity', 0) * 100, 2) if info.get('returnOnEquity') else 0,
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")
            return None
    
    def get_market_news(self, query: str = 'stocks', language: str = 'en', page_size: int = 10) -> List[Dict[str, Any]]:
        """
        Get market news using NewsAPI
        """
        if not self.news_api_key:
            print("News API key not found")
            return []
            
        try:
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': query,
                'language': language,
                'pageSize': page_size,
                'apiKey': self.news_api_key,
                'sortBy': 'publishedAt',
                'domains': 'bloomberg.com,reuters.com,cnbc.com,wsj.com,ft.com'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            articles = response.json().get('articles', [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'published_at': article.get('publishedAt', ''),
                    'image_url': article.get('urlToImage', '')
                })
                
            return formatted_articles
            
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []
    
    def get_watchlist_data(self) -> List[Dict[str, Any]]:
        """
        Get data for the watchlist (top 5 stocks)
        """
        watchlist = []
        for ticker in self.top_tickers[:5]:  # Get top 5 stocks
            stock_data = self.get_stock_data(ticker)
            if stock_data:
                watchlist.append(stock_data)
        return watchlist
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive market overview data including indices, market status, and crypto
        """
        try:
            # Get major indices data
            indices_data = self._get_indices_data()
            
            # Get market status (open/closed)
            market_status = self._get_market_status()
            
            # Get crypto market data
            crypto_data = self._get_crypto_market_data()
            
            # Get market sentiment
            market_sentiment = self._get_market_sentiment()
            
            # Get top gainers and losers
            gainers_losers = self._get_market_movers()
            
            return {
                'indices': indices_data,
                'market_status': market_status,
                'crypto': crypto_data,
                'sentiment': market_sentiment,
                'gainers': gainers_losers.get('gainers', []),
                'losers': gainers_losers.get('losers', []),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error in get_market_overview: {str(e)}")
            return {}
    
    def _get_indices_data(self) -> Dict[str, Dict[str, Any]]:
        """Get data for major market indices"""
        indices_data = {}
        
        for ticker, name in self.market_indices.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period='2d')
                
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change = current - previous
                    change_percent = (change / previous) * 100 if previous != 0 else 0
                    
                    indices_data[name] = {
                        'price': round(current, 2),
                        'change': round(change, 2),
                        'change_percent': round(change_percent, 2),
                        'is_positive': change >= 0,
                        'symbol': ticker
                    }
            except Exception as e:
                print(f"Error fetching {name} data: {str(e)}")
                indices_data[name] = {
                    'price': 0,
                    'change': 0,
                    'change_percent': 0,
                    'is_positive': True,
                    'symbol': ticker,
                    'error': str(e)
                }
        
        return indices_data
    
    def _get_market_status(self) -> Dict[str, Any]:
        """Get current market status (open/closed)"""
        try:
            # Using S&P 500 as a proxy for market status
            sp500 = yf.Ticker('^GSPC')
            hist = sp500.history(period='1d')
            
            now = datetime.now()
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            is_market_open = market_open <= now <= market_close and now.weekday() < 5
            
            return {
                'is_open': is_market_open,
                'open_time': market_open.strftime('%I:%M %p'),
                'close_time': market_close.strftime('%I:%M %p'),
                'current_time': now.strftime('%I:%M %p')
            }
        except Exception as e:
            print(f"Error getting market status: {str(e)}")
            return {'is_open': False, 'error': str(e)}
    
    def _get_crypto_market_data(self) -> Dict[str, Any]:
        """Get cryptocurrency market data"""
        try:
            # Using yfinance for crypto data
            btc = yf.Ticker('BTC-USD')
            eth = yf.Ticker('ETH-USD')
            
            btc_hist = btc.history(period='2d')
            eth_hist = eth.history(period='2d')
            
            def get_crypto_change(hist):
                if len(hist) >= 2:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[-2]
                    change = current - previous
                    change_percent = (change / previous) * 100 if previous != 0 else 0
                    return current, change, change_percent
                return 0, 0, 0
            
            btc_price, btc_change, btc_change_pct = get_crypto_change(btc_hist)
            eth_price, eth_change, eth_change_pct = get_crypto_change(eth_hist)
            
            # Get total crypto market cap (simplified)
            total_market_cap = btc.info.get('marketCap', 0) + eth.info.get('marketCap', 0)
            
            return {
                'total_market_cap': round(total_market_cap / 1e12, 2),  # in trillions
                'btc_price': round(btc_price, 2),
                'btc_change': round(btc_change, 2),
                'btc_change_pct': round(btc_change_pct, 2),
                'eth_price': round(eth_price, 2),
                'eth_change': round(eth_change, 2),
                'eth_change_pct': round(eth_change_pct, 2),
                'is_positive': btc_change_pct >= 0 or eth_change_pct >= 0
            }
            
        except Exception as e:
            print(f"Error getting crypto data: {str(e)}")
            return {
                'total_market_cap': 0,
                'btc_price': 0,
                'btc_change': 0,
                'btc_change_pct': 0,
                'eth_price': 0,
                'eth_change': 0,
                'eth_change_pct': 0,
                'is_positive': True,
                'error': str(e)
            }
    
    def _get_market_sentiment(self) -> Dict[str, Any]:
        """Get overall market sentiment"""
        try:
            # This is a simplified version - in a real app, you might use a sentiment analysis API
            # or calculate based on market indicators
            vix = yf.Ticker('^VIX')
            vix_data = vix.history(period='1d')
            
            vix_current = vix_data['Close'].iloc[-1] if not vix_data.empty else 20
            
            # VIX > 30 is considered high (bearish), < 20 is low (bullish)
            if vix_current > 30:
                sentiment = 'bearish'
                sentiment_score = -1
            elif vix_current < 20:
                sentiment = 'bullish'
                sentiment_score = 1
            else:
                sentiment = 'neutral'
                sentiment_score = 0
                
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'vix': round(vix_current, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting market sentiment: {str(e)}")
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0,
                'vix': 20,
                'error': str(e)
            }
    
    def _get_market_movers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get top market movers (gainers and losers)"""
        try:
            # Using yfinance's top gainers/losers
            gainers = []
            losers = []
            
            # Get top 5 gainers and losers from S&P 500
            sp500 = yf.Tickers('^GSPC')
            sp500_tickers = sp500.tickers
            
            # This is a simplified version - in a real app, you'd want to get actual gainers/losers
            # from a more comprehensive data source
            
            return {
                'gainers': gainers[:5],  # Top 5 gainers
                'losers': losers[:5]     # Top 5 losers
            }
            
        except Exception as e:
            print(f"Error getting market movers: {str(e)}")
            return {'gainers': [], 'losers': []}

# Singleton instance
stock_service = StockService()
