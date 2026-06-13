import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from langgraph.graph import StateGraph, END
from agent_state import AgentState
from config import llm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 데이터 로드
orders_df = pd.read_csv(os.path.join(BASE_DIR, "data", "orders.csv"))

def check_delivery(state: AgentState) -> AgentState:
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
    
    order_info = order.iloc[0]
    status = order_info["order_status"]
    
    # 배송 상태 한국어로 변환
    status_map = {
        "processing": "상품 준비중",
        "completed": "배송 완료",
        "cancelled": "주문 취소됨"
    }
    
    korean_status = status_map.get(status, status)
    
    answer = f"""
주문번호: {order_info['order_id']}
배송 상태: {korean_status}
주문일자: {order_info['order_date']}
    """
    
    return {**state, "answer": answer}

def create_delivery_agent():
    graph = StateGraph(AgentState)
    graph.add_node("check_delivery", check_delivery)
    graph.set_entry_point("check_delivery")
    graph.add_edge("check_delivery", END)
    return graph.compile()

if __name__ == "__main__":
    agent = create_delivery_agent()
    result = agent.invoke({
        "user_input": "O00000001 배송 어떻게 됐어요?",
        "category": "",
        "search_results": [],
        "answer": "",
        "escalate": False
    })
    print(result["answer"])