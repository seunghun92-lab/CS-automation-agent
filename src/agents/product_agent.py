import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from langgraph.graph import StateGraph, END
from agent_state import AgentState
from config import llm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 데이터 로드
products_df = pd.read_csv(os.path.join(BASE_DIR, "data", "products.csv"))

def search_product(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    
    # 상품명 추출
    prompt = f"""
    다음 문의에서 찾고 싶은 상품명이나 브랜드명을 추출하세요.
    없으면 "없음"이라고만 답하세요.
    
    문의: {user_input}
    """
    keyword = llm.invoke(prompt).content.strip()
    
    if keyword == "없음":
        return {**state, "answer": "찾으시는 상품명이나 브랜드명을 입력해 주세요."}
    
    # 상품 검색 (상품명 또는 브랜드명으로)
    results = products_df[
        products_df["product_name"].str.contains(keyword, case=False, na=False) |
        products_df["brand"].str.contains(keyword, case=False, na=False) |
        products_df["category"].str.contains(keyword, case=False, na=False)
    ].head(5)
    
    if results.empty:
        return {**state, "answer": f"'{keyword}' 관련 상품을 찾을 수 없습니다."}
    
    items_text = "\n".join([
        f"- {row['product_name']} ({row['brand']}) / 카테고리: {row['category']} / 가격: {row['price']}원 / 평점: {row['rating']}"
        for _, row in results.iterrows()
    ])
    
    answer = f"""
'{keyword}' 관련 상품 검색 결과입니다.

{items_text}
    """
    
    return {**state, "answer": answer}

def create_product_agent():
    graph = StateGraph(AgentState)
    graph.add_node("search_product", search_product)
    graph.set_entry_point("search_product")
    graph.add_edge("search_product", END)
    return graph.compile()

if __name__ == "__main__":
    agent = create_product_agent()
    result = agent.invoke({
        "user_input": "Nimbus 브랜드 상품 찾아줘",
        "category": "",
        "search_results": [],
        "answer": "",
        "escalate": False
    })
    print(result["answer"])