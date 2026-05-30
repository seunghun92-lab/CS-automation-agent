from config import vectorstore
from state import AgentState

def search_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]
    category = state["category"]
    
    # 카테고리 필터로 RAG 검색
    results = vectorstore.similarity_search(
        user_input,
        k=3,
        filter={"category": category}
    )
    
    # 검색 결과 없으면 전체에서 검색
    if not results:
        results = vectorstore.similarity_search(
            user_input,
            k=3
        )
    
    print(f"검색 결과 {len(results)}개 찾음")
    
    return {**state, "search_results": results}