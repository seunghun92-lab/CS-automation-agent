import json
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=True)

CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
FAQ_PATH = os.path.join(BASE_DIR, "data", "musinsa_faq.json")

def load_faq_data():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def create_vectorstore():
    faq_data = load_faq_data()
    
    documents = []
    for item in faq_data:
        doc = Document(
            page_content=f"Q: {item['question']}\nA: {item['answer']}",
            metadata={
                "category": item["category"],
                "question": item["question"]
            }
        )
        documents.append(doc)
    
    print(f"총 {len(documents)}개 문서 임베딩 시작...")
    
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    
    print("임베딩 완료!")
    return vectorstore

def search_faq(query, k=3):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    
    results = vectorstore.similarity_search(query, k=k)
    
    for i, doc in enumerate(results):
        print(f"\n=== 결과 {i+1} ===")
        print(f"카테고리: {doc.metadata['category']}")
        print(f"질문: {doc.metadata['question']}")
        print(f"답변: {doc.page_content[:100]}...")

if __name__ == "__main__":
    # create_vectorstore()
    search_faq("환불 어떻게 해요?")