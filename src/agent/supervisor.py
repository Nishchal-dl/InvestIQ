from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model

from src.agent.agents import json_parser_agent, news_agent, stock_agent

supervisor = create_supervisor(
    model=init_chat_model("openai:o4-mini"),
    agents=[stock_agent, news_agent, json_parser_agent],
    prompt=(
        "You are a supervisor managing three agents:\n"
        "- a stock agent. Assign stock-related tasks to this agent\n"
        "- a news agent. Assign news-related tasks to this agent\n"
        "- a json parser agent. Assign json parsing tasks to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile()

def prepare_human_message(ticker: str) -> str:
    return f"""
Analyze this stock data, financial information, recent news and provide your analysis in the requested JSON format.

STOCK DATA for {ticker.upper()}:

Provide your analysis in the exact JSON format specified, with no additional text.
"""

def invoke_supervisor(message: str) -> str:
    response = supervisor.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ]
    })
    
    import json

    lm = response['messages'][-1]
    return json.loads(lm.model_dump()['content'])

def query_supervisor(question: str) -> str:
    response = supervisor.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ]
    })
    return response['messages'][-1].content
