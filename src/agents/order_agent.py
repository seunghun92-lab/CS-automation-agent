import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from langgraph.graph import StateGraph, END
from agent_state import AgentState
from config import llm  # ← config에서 llm 가져오기

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 데이터 로드
orders_df = pd.read_csv(os.path.join(BASE_DIR, "data", "orders.csv"))
order_items_df = pd.read_csv(os.path.join(BASE_DIR, "data", "order_items.csv"))
products_df = pd.read_csv(os.path.join(BASE_DIR, "data", "products.csv"))

# order_items + products 조인
items_with_products = order_items_df.merge(products_df, on="product_id")

def search_order(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    
    # 주문번호 추출
    prompt = f"""
    다음 문의에서 주문번호만 추출하세요.
    주문번호 형식: O00000001 (O + 8자리 숫자)
    없으면 "없음"이라고만 답하세요.
    
    문의: {user_input}
    """
    order_id = llm.invoke(prompt).content.strip()
    
    if order_id == "없음":
        return {**state, "answer": "주문번호를 입력해 주세요. (예: O00000001)"}
    
    # 주문 조회
    order = orders_df[orders_df["order_id"] == order_id]
    
    if order.empty:
        return {**state, "answer": f"주문번호 {order_id}를 찾을 수 없습니다."}
    
    # 주문 상품 조회 (products 조인)
    items = items_with_products[items_with_products["order_id"] == order_id]
    
    order_info = order.iloc[0]
    items_text = "\n".join([
        f"- {row['product_name']} ({row['brand']}) / 수량: {row['quantity']}개 / 금액: {row['item_total']}원"
        for _, row in items.iterrows()
    ])
    
    answer = f"""
주문번호: {order_info['order_id']}
주문상태: {order_info['order_status']}
주문일자: {order_info['order_date']}
총금액: {order_info['total_amount']}원

주문 상품:
{items_text}
    """
    
    return {**state, "answer": answer}

def create_order_agent():
    graph = StateGraph(AgentState)
    graph.add_node("search_order", search_order)
    graph.set_entry_point("search_order")
    graph.add_edge("search_order", END)
    return graph.compile()


if __name__ == "__main__":
    agent = create_order_agent()
    result = agent.invoke({
        "user_input": "O00000001 주문 확인해줘",
        "category": "",
        "search_results": [],
        "answer": "",
        "escalate": False
    })
    print(result["answer"])