from config import vectorstore
from agent_state import AgentState

def search_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    
    # 카테고리 필터 제거하고 전체에서 검색
    results = vectorstore.similarity_search(
        user_input,
        k=3
    )
    
    print(f"검색 결과 {len(results)}개 찾음")
    
    return {**state, "search_results": results}