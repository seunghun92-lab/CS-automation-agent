from langgraph.graph import StateGraph, END
from agent_state import AgentState
from node.classify_node import classify_node
from node.search_node import search_node
from node.answer_node import answer_node
from node.escalate_node import escalate_node

def create_agent():
    # 그래프 생성
    graph = StateGraph(AgentState)
    
    # 노드 추가
    graph.add_node("classify", classify_node)
    graph.add_node("search", search_node)
    graph.add_node("answer", answer_node)
    graph.add_node("escalate", escalate_node)
    
    graph.set_entry_point("classify")
    
    graph.add_edge("classify", "search")
    graph.add_edge("search", "answer")
    
    graph.add_conditional_edges(
        "answer",
        lambda state: "escalate" if state["escalate"] else END,
        {
            "escalate": "escalate",
            END: END
        }
    )
    
    graph.add_edge("escalate", END)
    
    return graph.compile()

if __name__ == "__main__":
    agent = create_agent()
    
    result = agent.invoke({
        "user_input": "저 화가 많이 났어요 책임자 나오세요",
        "category": "",
        "search_results": [],
        "answer": "",
        "escalate": False
    })
    
    print("\n=== 최종 답변 ===")
    print(result["answer"])