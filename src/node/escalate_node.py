from agent_state import AgentState

def escalate_node(state: AgentState) -> AgentState:
    
    escalate_message = """
    안녕하세요. 고객님의 문의를 확인했습니다.
    해당 문의는 전문 상담원의 도움이 필요합니다.
    
    아래 방법으로 상담원과 연결하실 수 있습니다.
    
    ■ 1:1 문의
    무신사 앱 > 마이 > 1:1 문의
    
    ■ 고객센터
    운영시간: 평일 09:00 ~ 18:00
    
    빠른 시간 내에 도움드리겠습니다.
    """
    
    print("에스컬레이션 처리")
    
    return {**state, "answer": escalate_message}