from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
from pathlib import Path
env_path = Path(__file__).parent.parent.parent / '.env'
from dotenv import load_dotenv
load_dotenv(dotenv_path=env_path, override=True)
class RAGAgent:
    def __init__(self, data_dir):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.data_dir = data_dir
        self.agent = None
        self.documents = []
        self.load_data()
        self.chunk_documents()
        self.create_rag_agent()

    
    def load_data(self):
        pdf_files = [f for f in os.listdir(self.data_dir) if f.endswith('.pdf')]

        for pdf_file in pdf_files:
            file_path = os.path.join(self.data_dir, pdf_file)
            print(f"Loading {pdf_file}...")
            try:
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                self.documents.extend(pages)
                print(f"Loaded {len(pages)} pages from {pdf_file}")
            except Exception as e:
                print(f"Error loading {pdf_file}: {str(e)}")

    def chunk_documents(self, chunk_size=1000, chunk_overlap=200):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,  
            chunk_overlap=chunk_overlap,  
            add_start_index=True, 
        )

        all_splits = text_splitter.split_documents(self.documents)
        self.vector_store.add_documents(documents=all_splits)

    def create_rag_agent(self):
        from langchain.tools import tool

        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """Retrieve information to help answer a query."""
            retrieved_docs = self.vector_store.similarity_search(query, k=2)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
            )
            return serialized, retrieved_docs
        
        from langgraph.prebuilt import create_react_agent

        tools = [retrieve_context]
        prompt = """
            You have access to a tool that retrieves context from financial documents. 
            Use the tool to help answer user queries.
        """

        agent = create_react_agent(
            model="openai:o4-mini",
            tools=tools,
            prompt=(prompt),
            name="rag_agent"
        )

        self.agent = agent

    def query(self, query):
        if self.agent is None:
            raise ValueError("Agent not created. Call create_rag_agent first.")
        
        return self.agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )

rag_agent = RAGAgent(data_dir=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dataset", "Structured data-20250319T105519Z-001", "Structured data"))