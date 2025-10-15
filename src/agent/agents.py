from langgraph.prebuilt import create_react_agent
from typing import Dict, Any, List
from src.agent.tools import get_financial_data, get_news_articles, get_stock_data

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

class NewsSentiment(BaseModel):
    news_headline: str = Field(..., description="News Headline")
    time: str = Field(..., description="Time of the news. Friendly format like 1 week ago, 1 month ago, 1year ago")
    sentiment: float = Field(..., description="News rating between -1 and +1")

class SentimentAnalysis(BaseModel):
    key_words: List[str] = Field(..., description="Key words related to finance from recent news")
    news_sentiment: List[NewsSentiment] = Field(..., description="A list of news headlines and its sentiment")
    overall_sentiment_rating: float = Field(..., description="Overall sentiment of the company in the news, rated between -10 and +10")
    reasoning: str = Field(..., description="A one line reason for assigning the overall sentiment rating")

class StockRecommendation(BaseModel):
    recommendation: str = Field(..., description="Recommendation for the stock. Strong Buy, Buy, Hold, Sell, Strong Sell")
    reasoning: List[str] = Field(..., description="3 reasons for assigning the recommendation")
    price_prediction: float = Field(..., description="Predicted price of the stock")
    price_prediction_percentage: float = Field(..., description="Predicted price percentage change of the stock")

class RiskAssessment(BaseModel):
    market_risk: str = Field(..., description="Risk level of the stock. Low, Medium, High")
    volatility: str = Field(..., description="Volatility of the stock. Low, Medium, High")
    growth_potential: str = Field(..., description="Growth potential of the stock. Low, Medium, High")

class StockOverview(BaseModel):
    company_overview: str = Field(..., description="Financial summary of the company in a short paragraph")
    stock_recommendation: StockRecommendation = Field(..., description="Stock recommendation")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment")
    sentiment_analysis: SentimentAnalysis = Field(..., description="Sentiment analysis")

parser = JsonOutputParser(pydantic_object=StockOverview)

news_agent = create_react_agent(
    model="openai:o4-mini",
    tools=[get_news_articles],
    prompt=(
        "You are a news agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="news_agent",
)

stock_agent = create_react_agent(
    model="openai:o4-mini",
    tools=[get_stock_data, get_financial_data],
    prompt=(
        "You are a stock agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with stock-related tasks\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="stock_agent",
)


sys_msg = f"""
You are an expert financial analyst. Analyze the stock data and news, 
then respond with a comprehensive analysis in JSON format.

Response must be a valid JSON object matching this schema:
{parser.get_format_instructions()}

Guidelines:
- Be objective and data-driven
- Include both technical and fundamental analysis
- Consider recent news impact
- Provide clear, actionable recommendations
- overall sentiment rating score should reflect certainty (-10 to +10)
"""

json_parser_agent = create_react_agent(
    model="openai:o4-mini",
    tools=[],
    prompt=(sys_msg),
    name="json_parser_agent",
)
