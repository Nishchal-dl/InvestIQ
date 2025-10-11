# InvestIQ

InvestIQ is an application that uses AI to provide insights and recommendations for stocks.

It was developed as part of the Final Team Project 'Multi-Agent System' for the Natural Language Processing and GenAI (AAI-520-IN1) course, instructed by Azka Azka, Ph.D. from the University of San Diego.

## Installation

```bash
pip install -r requirements.txt
```

To run the financial_rag_agent notebook make sure to download the dataset from Kaggle [Financial Reports QA Dataset for RAG-based LLM Fin](https://www.kaggle.com/datasets/ahmedsta/data-retreiver) and place it in a folder called dataset at the root of the project.

The other 2 notebooks can be run without any additional setup but make sure to set the environment variables in the .env file (Refer to .env.example for the necessary variables).

## Usage
To run the flask app

```bash
python run.py
```
To run the induvidual notebooks

```bash
jupyter notebook <notebook_name>.ipynb
```

## Report
TBD