from config import llm
from agent_state import AgentState

def classify_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    
    prompt = f"""
    고객 문의를 아래 카테고리 중 하나로 분류해주세요.
    
    카테고리:
    - 배송
    - 취소/교환/반품
    - 상품/AS 문의
    - 주문/결제
    - 서비스
    - 이용 안내
    - 회원 정보
    - 기타
    
    고객 문의: {user_input}
    
    카테고리 이름만 답하세요.
    """
    
    response = llm.invoke(prompt)
    category = response.content.strip()
    
    print(f"분류 결과: {category}")
    
    return {**state, "category": category}