import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from agent_state import AgentState

from agent import create_agent
from agents.order_agent import create_order_agent
from agents.product_agent import create_product_agent
from agents.delivery_agent import create_delivery_agent

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"), override=True)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 각 에이전트 초기화
cs_agent = create_agent()
order_agent = create_order_agent()
product_agent = create_product_agent()
delivery_agent = create_delivery_agent()

def route_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    
    prompt = f"""
    고객 문의를 보고 어떤 에이전트로 라우팅할지 결정하세요.
    
    에이전트 종류:
    - cs_agent: 일반 CS 문의 (환불정책, 교환방법 등 FAQ)
    - order_agent: 주문 조회/확인 (주문번호 포함)
    - product_agent: 상품 검색/정보
    - delivery_agent: 배송 조회 (주문번호 포함)
    
    고객 문의: {user_input}
    
    에이전트 이름만 답하세요.
    """
    
    agent_name = llm.invoke(prompt).content.strip()
    print(f"라우팅 결과: {agent_name}")
    
    return {**state, "category": agent_name}

def execute_agent(state: AgentState) -> AgentState:
    agent_name = state["category"]
    
    if agent_name == "order_agent":
        result = order_agent.invoke(state)
    elif agent_name == "product_agent":
        result = product_agent.invoke(state)
    elif agent_name == "delivery_agent":
        result = delivery_agent.invoke(state)
    else:
        result = cs_agent.invoke(state)
    
    return {**state, "answer": result["answer"]}

def create_orchestrator():
    graph = StateGraph(AgentState)
    
    graph.add_node("route", route_node)
    graph.add_node("execute", execute_agent)
    
    graph.set_entry_point("route")
    graph.add_edge("route", "execute")
    graph.add_edge("execute", END)
    
    return graph.compile()

if __name__ == "__main__":
    orchestrator = create_orchestrator()
    
    test_questions = [
        "O00000001 주문 확인해줘",
        "환불하고 싶어요",
        "Nimbus 브랜드 상품 찾아줘",
        "O00000002 배송 어떻게 됐어요?"
    ]
    
    for question in test_questions:
        print(f"\n질문: {question}")
        result = orchestrator.invoke({
            "user_input": question,
            "category": "",
            "search_results": [],
            "answer": "",
            "escalate": False
        })
        print(f"답변: {result['answer']}")
        print("="*50)