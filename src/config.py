import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv(dotenv_path="../.env", override=True)

# LLM 설정
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

# 임베딩 모델
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 벡터스토어
vectorstore = Chroma(
    persist_directory="../data/chroma_db",
    embedding_function=embeddings
)