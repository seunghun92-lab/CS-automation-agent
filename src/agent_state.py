from typing import TypedDict, List

class AgentState(TypedDict):
    user_input: str
    category : str
    search_results : List
    answer : str
    escalate : bool