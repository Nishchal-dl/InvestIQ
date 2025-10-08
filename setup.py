from setuptools import setup, find_packages

setup(
    name="investiq",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'flask==3.0.0',
        'python-dotenv==1.0.0',
        'langchain==0.0.335',
        'langgraph==0.0.1',
        'requests==2.31.0',
        'gunicorn==21.2.0',
        'openai==1.3.0',
    ],
    python_requires='>=3.8',
)
