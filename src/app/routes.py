from flask import Blueprint, render_template, jsonify, request, current_app
from datetime import datetime, timedelta
import random
import json
import time
from functools import wraps
from flask_caching import Cache
from src.agent.supervisor import invoke_supervisor

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import services
import sys
sys.path.append(str(Path(__file__).parent.parent))
from services.stock_service import stock_service

main = Blueprint('main', __name__)

def init_app(app):
    """Initialize the application"""
    return app

# Extended mock data for demonstration
mock_stock_data = {
    'AAPL': {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'exchange': 'NASDAQ',
        'industry': 'Consumer Electronics',
        'sector': 'Technology',
        'ceo': 'Tim Cook',
        'employees': 164000,
        'city': 'Cupertino',
        'country': 'United States',
        'founded': 1976,
        'website': 'https://www.apple.com',
        'description': 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The company offers iPhone, a line of smartphones; Mac, a line of personal computers; iPad, a line of multi-purpose tablets; and wearables, home, and accessories comprising AirPods, Apple TV, Apple Watch, Beats products, and HomePod.',
        'price': 187.68,
        'change': 2.35,
        'change_percent': 1.27,
        'market_cap': 2945.23,
        'pe_ratio': 32.15,
        'eps': 5.84,
        'dividend_yield': 0.52,
        'week52_high': 198.23,
        'week52_low': 124.17,
        'avg_volume': 57892345,
        'shares_outstanding': 15680000000,
        'revenue_ttm': 394328000000,
        'gross_profit': 169559000000,
        'profit_margin': 0.2534,
        'return_on_equity': 1.46,
        'analyst_ratings': {
            'strong_buy': 15,
            'buy': 22,
            'hold': 8,
            'sell': 1,
            'strong_sell': 0,
            'total': 46
        },
        'analyst_consensus': {
            'rating': 'Buy',
            'price_target': 205.50,
            'high': 235.00,
            'low': 180.00
        }
    },
    'MSFT': {
        'symbol': 'MSFT',
        'name': 'Microsoft Corporation',
        'exchange': 'NASDAQ',
        'industry': 'Software—Infrastructure',
        'sector': 'Technology',
        'ceo': 'Satya Nadella',
        'employees': 221000,
        'city': 'Redmond',
        'country': 'United States',
        'founded': 1975,
        'website': 'https://www.microsoft.com',
        'description': 'Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide. The company operates in three segments: Productivity and Business Processes, Intelligent Cloud, and More Personal Computing.',
        'price': 425.52,
        'change': -1.24,
        'change_percent': -0.29,
        'market_cap': 3162.45,
        'pe_ratio': 36.78,
        'eps': 11.57,
        'dividend_yield': 0.71,
        'week52_high': 440.82,
        'week52_low': 275.37,
        'avg_volume': 25678923,
        'shares_outstanding': 7434000000,
        'revenue_ttm': 218310000000,
        'gross_profit': 135620000000,
        'profit_margin': 0.3642,
        'return_on_equity': 0.39,
        'analyst_ratings': {
            'strong_buy': 32,
            'buy': 18,
            'hold': 5,
            'sell': 1,
            'strong_sell': 0,
            'total': 56
        },
        'analyst_consensus': {
            'rating': 'Strong Buy',
            'price_target': 450.75,
            'high': 500.00,
            'low': 400.00
        }
    },
    'GOOGL': {
        'symbol': 'GOOGL',
        'name': 'Alphabet Inc.',
        'exchange': 'NASDAQ',
        'industry': 'Internet Content & Information',
        'sector': 'Communication Services',
        'ceo': 'Sundar Pichai',
        'employees': 190234,
        'city': 'Mountain View',
        'country': 'United States',
        'founded': 1998,
        'website': 'https://abc.xyz',
        'description': 'Alphabet Inc. provides online advertising services in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America. The company offers performance and brand advertising services. It operates through Google Services, Google Cloud, and Other Bets segments.',
        'price': 175.22,
        'change': 0.87,
        'change_percent': 0.50,
        'market_cap': 2215.67,
        'pe_ratio': 28.93,
        'eps': 6.05,
        'dividend_yield': 0.00,
        'week52_high': 182.94,
        'week52_low': 101.86,
        'avg_volume': 32789123,
        'shares_outstanding': 12650000000,
        'revenue_ttm': 307394000000,
        'gross_profit': 174142000000,
        'profit_margin': 0.2134,
        'return_on_equity': 0.28,
        'analyst_ratings': {
            'strong_buy': 28,
            'buy': 24,
            'hold': 6,
            'sell': 2,
            'strong_sell': 1,
            'total': 61
        },
        'analyst_consensus': {
            'rating': 'Buy',
            'price_target': 185.25,
            'high': 210.00,
            'low': 160.00
        }
    },
    'AMZN': {
        'symbol': 'AMZN',
        'name': 'Amazon.com, Inc.',
        'exchange': 'NASDAQ',
        'industry': 'Internet Retail',
        'sector': 'Consumer Cyclical',
        'ceo': 'Andrew Jassy',
        'employees': 1608000,
        'city': 'Seattle',
        'country': 'United States',
        'founded': 1994,
        'website': 'https://www.amazon.com',
        'description': 'Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally. The company operates through three segments: North America, International, and Amazon Web Services (AWS).',
        'price': 185.19,
        'change': 1.23,
        'change_percent': 0.67,
        'market_cap': 1925.34,
        'pe_ratio': 62.45,
        'eps': 2.96,
        'dividend_yield': 0.00,
        'week52_high': 189.77,
        'week52_low': 101.15,
        'avg_volume': 45678912,
        'shares_outstanding': 10400000000,
        'revenue_ttm': 574785000000,
        'gross_profit': 225152000000,
        'profit_margin': 0.0276,
        'return_on_equity': 0.15,
        'analyst_ratings': {
            'strong_buy': 42,
            'buy': 18,
            'hold': 3,
            'sell': 1,
            'strong_sell': 0,
            'total': 64
        },
        'analyst_consensus': {
            'rating': 'Strong Buy',
            'price_target': 210.50,
            'high': 230.00,
            'low': 190.00
        }
    },
    'TSLA': {
        'symbol': 'TSLA',
        'name': 'Tesla, Inc.',
        'exchange': 'NASDAQ',
        'industry': 'Auto Manufacturers',
        'sector': 'Consumer Cyclical',
        'ceo': 'Elon Musk',
        'employees': 127855,
        'city': 'Austin',
        'country': 'United States',
        'founded': 2003,
        'website': 'https://www.tesla.com',
        'description': 'Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally. The company operates in two segments, Automotive, and Energy Generation and Storage.',
        'price': 252.64,
        'change': -3.21,
        'change_percent': -1.25,
        'market_cap': 802.45,
        'pe_ratio': 68.92,
        'eps': 3.66,
        'dividend_yield': 0.00,
        'week52_high': 313.80,
        'week52_low': 138.80,
        'avg_volume': 98765432,
        'shares_outstanding': 3175000000,
        'revenue_ttm': 98650000000,
        'gross_profit': 20890000000,
        'profit_margin': 0.1032,
        'return_on_equity': 0.29,
        'analyst_ratings': {
            'strong_buy': 12,
            'buy': 15,
            'hold': 18,
            'sell': 8,
            'strong_sell': 5,
            'total': 58
        },
        'analyst_consensus': {
            'rating': 'Hold',
            'price_target': 240.75,
            'high': 380.00,
            'low': 150.00
        }
    },
    'NVDA': {
        'symbol': 'NVDA',
        'name': 'NVIDIA Corporation',
        'exchange': 'NASDAQ',
        'industry': 'Semiconductors',
        'sector': 'Technology',
        'ceo': 'Jensen Huang',
        'employees': 26400,
        'city': 'Santa Clara',
        'country': 'United States',
        'founded': 1993,
        'website': 'https://www.nvidia.com',
        'description': 'NVIDIA Corporation provides graphics, and compute and networking solutions in the United States, Taiwan, China, and internationally. The company operates through Graphics, Compute & Networking segments.',
        'price': 950.02,
        'change': 25.45,
        'change_percent': 2.75,
        'market_cap': 2345.67,
        'pe_ratio': 76.45,
        'eps': 12.43,
        'dividend_yield': 0.02,
        'week52_high': 974.00,
        'week52_low': 222.97,
        'avg_volume': 45678901,
        'shares_outstanding': 2468000000,
        'revenue_ttm': 60922000000,
        'gross_profit': 44351000000,
        'profit_margin': 0.4876,
        'return_on_equity': 0.88,
        'analyst_ratings': {
            'strong_buy': 38,
            'buy': 22,
            'hold': 5,
            'sell': 1,
            'strong_sell': 0,
            'total': 66
        },
        'analyst_consensus': {
            'rating': 'Strong Buy',
            'price_target': 1050.25,
            'high': 1200.00,
            'low': 900.00
        }
    }
}

def get_mock_news(symbol):
    companies = {
        'AAPL': 'Apple',
        'MSFT': 'Microsoft',
        'GOOGL': 'Google',
        'AMZN': 'Amazon',
        'TSLA': 'Tesla',
        'NVDA': 'NVIDIA'
    }
    company = companies.get(symbol, 'the company')
    
    # Define some common tags based on company
    company_tags = {
        'AAPL': ['Technology', 'Consumer Electronics', 'Innovation'],
        'MSFT': ['Software', 'Cloud', 'Enterprise'],
        'GOOGL': ['Internet', 'Search', 'Advertising'],
        'AMZN': ['E-commerce', 'Cloud', 'Retail'],
        'TSLA': ['Electric Vehicles', 'Clean Energy', 'Automotive'],
        'NVDA': ['Semiconductors', 'AI', 'Gaming']
    }
    
    tags = company_tags.get(symbol, ['Business', 'Finance', 'Technology'])
    
    news_items = [
        {
            'title': f"{company} announces breakthrough in AI technology",
            'source': 'Tech News',
            'published_at': (datetime.now() - timedelta(hours=2)).isoformat() + 'Z',
            'summary': f"{company} has unveiled a new AI system that could revolutionize the tech industry. Analysts are calling it a game-changer for the company's future growth prospects.",
            'url': '#',
            'image_url': f'https://source.unsplash.com/random/600x400/?{company.lower()},technology,1',
            'tags': tags + ['AI', 'Innovation']
        },
        {
            'title': f"Analysts raise price target for {company} stock",
            'source': 'Financial Times',
            'published_at': (datetime.now() - timedelta(days=1)).isoformat() + 'Z',
            'summary': f"Several analysts have increased their price targets for {company} following strong earnings that beat Wall Street expectations. The stock is now a top pick for many funds.",
            'url': '#',
            'image_url': f'https://source.unsplash.com/random/600x400/?{company.lower()},finance,2',
            'tags': tags + ['Earnings', 'Analysis'],
            'sentiment': 0.9  # Very positive sentiment
        },
        {
            'title': f"{company} partners with leading tech firms on new initiative",
            'source': 'Business Insider',
            'published_at': (datetime.now() - timedelta(days=2)).isoformat() + 'Z',
            'summary': f"{company} has announced a strategic partnership with other tech giants to develop new industry standards that could shape the future of technology for years to come.",
            'url': '#',
            'image_url': f'https://source.unsplash.com/random/600x400/?{company.lower()},business,3',
            'tags': tags + ['Partnership', 'Innovation'],
            'sentiment': 0.6  # Slightly positive sentiment
        },
        {
            'title': f"{company} expands into new markets with latest acquisition",
            'source': 'Wall Street Journal',
            'published_at': (datetime.now() - timedelta(days=3)).isoformat() + 'Z',
            'summary': f"In a move that surprised many analysts, {company} has acquired a smaller competitor, signaling its intention to expand into new and emerging markets.",
            'url': '#',
            'image_url': f'https://source.unsplash.com/random/600x400/?{company.lower()},office,4',
            'tags': tags + ['Acquisition', 'Expansion'],
            'sentiment': 0.4  # Neutral to slightly positive sentiment
        },
        {
            'title': f"{company} CEO outlines vision for the future at annual conference",
            'source': 'CNBC',
            'published_at': (datetime.now() - timedelta(days=4)).isoformat() + 'Z',
            'summary': f"At the annual shareholder meeting, {company}'s CEO shared an ambitious vision for the company's future, including new product lines and market expansions.",
            'url': '#',
            'image_url': f'https://source.unsplash.com/random/600x400/?{company.lower()},conference,5',
            'tags': tags + ['Leadership', 'Strategy'],
            'sentiment': 0.7  # Positive sentiment
        }
    ]
    
    # Return a random selection of 3 news items with unique titles
    unique_news = {}
    for item in news_items:
        if item['title'] not in unique_news:
            unique_news[item['title']] = item
    
    # Ensure we have at least 3 unique news items
    if len(unique_news) >= 3:
        return random.sample(list(unique_news.values()), 3)
    return list(unique_news.values())

@main.route('/')
@main.route('/dashboard')
def dashboard():
    try:
        # Get watchlist data (top 5 stocks for the dashboard)
        watchlist = stock_service.get_watchlist_data()
        
        # Get market overview data
        market_overview = stock_service.get_market_overview()
        
        # Get recent market news
        recent_news = stock_service.get_market_news(query='stocks', page_size=6)
        
        # Get AI insights (you can implement this later)
        ai_insights = {
            'market_sentiment': 'positive',
            'trending_stocks': ['NVDA', 'TSLA', 'AMD'],
            'sector_performance': {
                'Technology': 1.5,
                'Healthcare': 0.8,
                'Finance': 0.3,
                'Energy': -0.5,
                'Consumer': 0.7
            }
        }
        
        
        return render_template(
            'dashboard.html',
            watchlist=watchlist,
            market_overview=market_overview,
            recent_news=recent_news,
            ai_insights=ai_insights,
        )
        
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        # Fallback to mock data in case of error
        watchlist = [
            mock_stock_data['AAPL'],
            mock_stock_data['MSFT'],
            mock_stock_data['GOOGL'],
            mock_stock_data['AMZN'],
            mock_stock_data['TSLA']
        ]
        
        # Get recent news (mix of all companies)
        all_news = []
        for symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA']:
            all_news.extend(get_mock_news(symbol))
        
        # Sort by published_at date and get the 6 most recent
        recent_news = sorted(all_news, key=lambda x: x['published_at'], reverse=True)[:6]
        
        return render_template(
            'dashboard.html',
            watchlist=watchlist,
            market_overview={},
            recent_news=recent_news,
            ai_insights={},
            recent_activity=[]
        )
    return render_template('dashboard.html', watchlist=watchlist, news=recent_news)

def get_stock_analysis(symbol):
    """Helper function to get stock analysis from supervisor agent with caching"""
    from .cache import cache
    
    # Create a cache key
    cache_key = f'stock_analysis_{symbol}'
    
    # Try to get from cache first
    analysis = cache.get(cache_key)
    if analysis is not None:
        current_app.logger.info(f"Cache hit for {symbol}")
        return analysis
        
    try:
        current_app.logger.info(f"Cache miss for {symbol}, fetching from supervisor")
        analysis = invoke_supervisor(symbol)
        if not analysis:
            raise ValueError(f"No analysis returned for {symbol}")
            
        # Store in cache with 30 min expiration
        cache.set(cache_key, analysis, timeout=1800)
        return analysis
        
    except Exception as e:
        current_app.logger.error(f"Error in get_stock_analysis for {symbol}: {str(e)}")
        return None

@main.route('/stock/<symbol>')
def stock_detail(symbol):
    symbol = symbol.upper()
    stock = mock_stock_data.get(symbol)
    
    if not stock:
        # If stock not found, use a default one (for demo purposes)
        stock = mock_stock_data['AAPL'].copy()
        stock['symbol'] = symbol
        stock['name'] = f"{symbol} Company Inc."
        stock['exchange'] = 'NASDAQ'
        stock['industry'] = 'Technology'
        stock['sector'] = 'Technology'
        stock['ceo'] = 'John Smith'
        stock['employees'] = 10000
        stock['city'] = 'San Francisco'
        stock['country'] = 'United States'
        stock['founded'] = 2000
    
    # Get fresh analysis
    analysis = get_stock_analysis(symbol)
    print(analysis)
    # Get recent news for the stock
    recent_news = get_mock_news(symbol)[:5]  # Get first 5 news items
    
    # Prepare default values in case analysis is None
    default_analysis = {
        'sentiment_analysis': {},
        'company_overview': 'Analysis not available at the moment. Please try again later.',
        'stock_recommendation': {
            'recommendation': 'N/A',
            'confidence': 0,
            'reasoning': 'Analysis in progress...'
        },
        'risk_assessment': {
            'level': 'Medium',
            'factors': ['Market data not available'],
            'score': 5
        }
    }
    
    if analysis is None:
        current_app.logger.warning(f"No analysis available for {symbol}, using defaults")
        analysis = default_analysis
    
    # Prepare the context for the template
    context = {
        'stock': stock,
        'recent_news': recent_news,
        'ai_sentiment': analysis.get('sentiment_analysis', {}),
        'sentiment_events': analysis.get('sentiment_analysis', {}).get('news_sentiment', []),
        'company_overview': analysis.get('company_overview', default_analysis['company_overview']),
        'stock_recommendation': analysis.get('stock_recommendation', default_analysis['stock_recommendation']),
        'risk_assessment': analysis.get('risk_assessment', default_analysis['risk_assessment'])
    }
    
    # Add any additional stock details
    stock['website'] = '#'
    stock['description'] = f"{symbol} is a leading technology company specializing in innovative solutions for the modern digital age."
    
    # Add the stock to the context
    context['stock'] = stock
    
    return render_template('stock_detail.html', **context)

@main.route('/api/stock/<symbol>')
def stock_data(symbol):
    symbol = symbol.upper()
    stock = mock_stock_data.get(symbol, {})
    return jsonify(stock)

@main.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@main.route('/ai-chat')
def ai_chat():
    """Render the AI chat interface."""
    return render_template('ai_chat.html')

@main.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chat messages and return AI responses."""
    data = request.get_json()
    user_message = data.get('message', '').lower()
    
    # Simple response logic - in a real app, this would call an LLM API
    responses = {
        'hello': "Hello! I'm your AI investment assistant. How can I help you with your investments today?",
        'hi': "Hi there! I'm here to help with your investment questions. What would you like to know?",
        'what stocks should i buy': "I can't provide specific investment advice, but I can help you research stocks. What type of companies are you interested in?",
        'how to start investing': "To start investing, consider these steps: 1) Set clear financial goals 2) Build an emergency fund 3) Pay off high-interest debt 4) Start with index funds or ETFs 5) Diversify your portfolio. Would you like more details on any of these steps?",
        'market trend': "I currently don't have real-time market data, but I can help you analyze specific stocks or sectors. What would you like to know more about?",
        'portfolio': "To help you with your portfolio, I'd need to know what investments you currently hold and what your financial goals are. Would you like to discuss a specific aspect of portfolio management?",
        'risk': "Investment risk varies by asset class. Generally, stocks are riskier than bonds, but offer higher potential returns. Your risk tolerance depends on your investment timeline and financial goals. What's your investment horizon?",
        'retirement': "For retirement planning, consider: 1) Contributing to tax-advantaged accounts like 401(k) or IRA 2) Asset allocation based on your age and risk tolerance 3) Regular contributions 4) Rebalancing periodically. Would you like more details on any of these areas?",
        'crypto': "Cryptocurrencies are highly volatile and speculative investments. They can offer high returns but come with significant risk. It's generally recommended to allocate only a small portion of your portfolio to crypto if you choose to invest. Would you like to discuss risk management strategies?",
        'dividend': "Dividend investing focuses on stocks that pay regular dividends. These are often well-established companies with stable cash flows. Key metrics to consider include dividend yield, payout ratio, and dividend growth history. Would you like help analyzing specific dividend stocks?"
    }
    
    # Find the best matching response
    response = ""
    for keyword, resp in responses.items():
        if keyword in user_message:
            response = resp
            break
    
    # Default response if no keyword matches
    if not response:
        response = "I'm here to help with your investment questions. Could you provide more details about what you'd like to know? I can help with stock analysis, portfolio strategies, market trends, and general investment advice."
    
    # Simulate processing time
    time.sleep(1)
    
    return jsonify({
        'response': response,
        'timestamp': datetime.utcnow().isoformat()
    })
