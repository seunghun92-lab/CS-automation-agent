from config import llm
from agent_state import AgentState

def answer_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    search_results = state["search_results"]
    retry_count = state.get("retry_count", 0)
    
    # 검색 결과 없으면 바로 에스컬레이션
    if not search_results:
        return {**state, "answer": "상담원 연결이 필요합니다", "escalate": True, "retry_count": retry_count}
    
    context = "\n\n".join([doc.page_content for doc in search_results])
    
    prompt = f"""
    당신은 무신사 고객센터 AI 상담원입니다.
    아래 FAQ 내용을 참고하여 고객 문의에 답변해주세요.
    
    FAQ 내용:
    {context}
    
    고객 문의: {user_input}
    
    답변 규칙:
    1. FAQ 내용을 기반으로 답변하세요
    2. 친절하고 명확하게 답변하세요
    3. FAQ에 없는 내용은 답변하지 마세요
    4. FAQ로 해결이 어려우면 "상담원 연결이 필요합니다"라고 답하세요
    5. 고객이 화났거나 책임자/상담원을 요청하면 반드시 "상담원 연결이 필요합니다"라고 답하세요
    """
    
    response = llm.invoke(prompt)
    answer = response.content.strip()
    
    # 에스컬레이션 여부
    escalate = "상담원 연결이 필요합니다" in answer
    
    # 답변 품질 낮으면 재검색 (최대 2회)
    retry = False
    if retry_count < 2:
        if "모르" in answer or "없습니다" in answer or "확인이 어렵" in answer:
            retry = True
    
    print(f"답변 생성 완료 (retry_count: {retry_count}, retry: {retry})")
    print(f"에스컬레이션: {escalate}")
    
    return {**state, "answer": answer, "escalate": escalate, "retry": retry, "retry_count": retry_count + 1}