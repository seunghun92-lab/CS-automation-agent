import csv
import os
from langgraph.graph import StateGraph, END
from agent_state import AgentState
from node.classify_node import classify_node
from node.search_node import search_node
from node.answer_node import answer_node
from node.escalate_node import escalate_node
from config import langfuse_handler

def create_agent():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_node)
    graph.add_node("search", search_node)
    graph.add_node("answer", answer_node)
    graph.add_node("escalate", escalate_node)
    graph.set_entry_point("classify")
    graph.add_edge("classify", "search")
    graph.add_edge("search", "answer")
    graph.add_conditional_edges(
        "answer",
        lambda state: "escalate" if state["escalate"] else ("search" if state.get("retry") else END),
        {"escalate": "escalate", "search": "search", END: END}
    )
    graph.add_edge("escalate", END)
    return graph.compile()

test_cases = [
    # 환불/반품 (15개)
    {"question": "환불하고 싶어요", "expected_escalate": False, "expected_keyword": "반품", "category": "환불/반품"},
    {"question": "반품 어떻게 해요?", "expected_escalate": False, "expected_keyword": "반품", "category": "환불/반품"},
    {"question": "교환 신청하고 싶어요", "expected_escalate": False, "expected_keyword": "교환", "category": "환불/반품"},
    {"question": "반품 비용이 얼마예요?", "expected_escalate": False, "expected_keyword": "배송비", "category": "환불/반품"},
    {"question": "환불 언제 돼요?", "expected_escalate": False, "expected_keyword": "환불", "category": "환불/반품"},
    {"question": "상품 받았는데 불량이에요", "expected_escalate": False, "expected_keyword": "반품", "category": "환불/반품"},
    {"question": "교환 기간이 얼마예요?", "expected_escalate": False, "expected_keyword": "7일", "category": "환불/반품"},
    {"question": "반품 접수는 어떻게 해요?", "expected_escalate": False, "expected_keyword": "반품", "category": "환불/반품"},
    {"question": "환불 금액이 언제 입금되나요?", "expected_escalate": False, "expected_keyword": "환불", "category": "환불/반품"},
    {"question": "부분 취소 가능한가요?", "expected_escalate": False, "expected_keyword": "취소", "category": "환불/반품"},
    {"question": "교환 배송비는 누가 내나요?", "expected_escalate": False, "expected_keyword": "배송비", "category": "환불/반품"},
    {"question": "반품 후 환불까지 얼마나 걸려요?", "expected_escalate": False, "expected_keyword": "환불", "category": "환불/반품"},
    {"question": "단순변심으로 반품 가능한가요?", "expected_escalate": False, "expected_keyword": "반품", "category": "환불/반품"},
    {"question": "택 제거한 상품도 반품 되나요?", "expected_escalate": False, "expected_keyword": "반품", "category": "환불/반품"},
    {"question": "바로 환불 서비스가 뭐예요?", "expected_escalate": False, "expected_keyword": "환불", "category": "환불/반품"},

    # 배송 (15개)
    {"question": "배송이 언제 와요?", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "배송 조회 어떻게 해요?", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "송장번호 확인하고 싶어요", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "배송지 변경할 수 있나요?", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "배송이 너무 늦어요", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "택배사 연락처 알려주세요", "expected_escalate": False, "expected_keyword": "택배", "category": "배송"},
    {"question": "상품이 아직 안 왔어요", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "배송 완료인데 못 받았어요", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "무배당발 서비스가 뭐예요?", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "송장 흐름이 안 보여요", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "배송 지연 보상 받을 수 있나요?", "expected_escalate": False, "expected_keyword": "보상", "category": "배송"},
    {"question": "상품이 파손되어 왔어요", "expected_escalate": False, "expected_keyword": "반품", "category": "배송"},
    {"question": "일반 배송은 며칠 걸려요?", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "예약 배송 상품은 언제 와요?", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},
    {"question": "주문한 상품이 일부만 왔어요", "expected_escalate": False, "expected_keyword": "배송", "category": "배송"},

    # 주문/결제 (15개)
    {"question": "주문 취소하고 싶어요", "expected_escalate": False, "expected_keyword": "취소", "category": "주문/결제"},
    {"question": "결제가 안 돼요", "expected_escalate": False, "expected_keyword": "결제", "category": "주문/결제"},
    {"question": "적립금 사용법 알려줘", "expected_escalate": False, "expected_keyword": "적립금", "category": "주문/결제"},
    {"question": "쿠폰 어떻게 써요?", "expected_escalate": False, "expected_keyword": "쿠폰", "category": "주문/결제"},
    {"question": "카드 결제 가능한가요?", "expected_escalate": False, "expected_keyword": "결제", "category": "주문/결제"},
    {"question": "무통장 입금 어떻게 해요?", "expected_escalate": False, "expected_keyword": "계좌", "category": "주문/결제"},
    {"question": "영수증 발급 가능한가요?", "expected_escalate": False, "expected_keyword": "영수증", "category": "주문/결제"},
    {"question": "포인트 적립은 어떻게 돼요?", "expected_escalate": False, "expected_keyword": "적립", "category": "주문/결제"},
    {"question": "주문 내역 확인하고 싶어요", "expected_escalate": False, "expected_keyword": "주문", "category": "주문/결제"},
    {"question": "무신사페이가 뭐예요?", "expected_escalate": False, "expected_keyword": "결제", "category": "주문/결제"},
    {"question": "가상계좌 결제 어떻게 해요?", "expected_escalate": False, "expected_keyword": "계좌", "category": "주문/결제"},
    {"question": "휴대폰 결제 가능한가요?", "expected_escalate": False, "expected_keyword": "결제", "category": "주문/결제"},
    {"question": "적립금 선할인이 뭐예요?", "expected_escalate": False, "expected_keyword": "적립금", "category": "주문/결제"},
    {"question": "상품권 어떻게 사용해요?", "expected_escalate": False, "expected_keyword": "상품권", "category": "주문/결제"},
    {"question": "결제 수단이 뭐가 있어요?", "expected_escalate": False, "expected_keyword": "결제", "category": "주문/결제"},

    # 회원 (15개)
    {"question": "비밀번호 찾고 싶어요", "expected_escalate": False, "expected_keyword": "비밀번호", "category": "회원"},
    {"question": "회원 탈퇴하고 싶어요", "expected_escalate": False, "expected_keyword": "탈퇴", "category": "회원"},
    {"question": "회원 등급이 어떻게 돼요?", "expected_escalate": False, "expected_keyword": "등급", "category": "회원"},
    {"question": "아이디 찾고 싶어요", "expected_escalate": False, "expected_keyword": "아이디", "category": "회원"},
    {"question": "생일 쿠폰은 언제 오나요?", "expected_escalate": False, "expected_keyword": "쿠폰", "category": "회원"},
    {"question": "개인정보 변경하고 싶어요", "expected_escalate": False, "expected_keyword": "정보", "category": "회원"},
    {"question": "소셜 로그인 연동하고 싶어요", "expected_escalate": False, "expected_keyword": "로그인", "category": "회원"},
    {"question": "적립금 유효기간이 있나요?", "expected_escalate": False, "expected_keyword": "적립금", "category": "회원"},
    {"question": "회원가입 어떻게 해요?", "expected_escalate": False, "expected_keyword": "가입", "category": "회원"},
    {"question": "본인인증 어떻게 해요?", "expected_escalate": False, "expected_keyword": "인증", "category": "회원"},
    {"question": "적립금 소멸 예정 알림 받았어요", "expected_escalate": False, "expected_keyword": "적립금", "category": "회원"},
    {"question": "카카오 로그인 연동하고 싶어요", "expected_escalate": False, "expected_keyword": "로그인", "category": "회원"},
    {"question": "회원 탈퇴 취소하고 싶어요", "expected_escalate": False, "expected_keyword": "탈퇴", "category": "회원"},
    {"question": "등급 쿠폰 어디서 확인해요?", "expected_escalate": False, "expected_keyword": "쿠폰", "category": "회원"},
    {"question": "포인트 확인하고 싶어요", "expected_escalate": False, "expected_keyword": "포인트", "category": "회원"},

    # 환각 테스트 (20개)
    {"question": "무신사에서 아이폰 살 수 있나요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "대표이사가 누구예요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "내일 날씨 어때요?", "expected_escalate": False, "expected_keyword": "제공", "category": "환각"},
    {"question": "무신사 주가가 얼마예요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "로또 번호 알려줘", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "환불 기간이 100일이에요?", "expected_escalate": False, "expected_keyword": "7일", "category": "환각"},
    {"question": "무신사 창업일이 언제예요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "직원수가 몇명이에요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "경쟁사 정보 알려줘", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "무신사 연매출이 얼마예요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "배송비가 1000원이에요?", "expected_escalate": False, "expected_keyword": "배송", "category": "환각"},
    {"question": "반품 기간이 30일 맞죠?", "expected_escalate": False, "expected_keyword": "7일", "category": "환각"},
    {"question": "삼성전자 주식 알려줘", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "오늘 점심 뭐 먹을까요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "무신사 본사 주소가 어디예요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "적립금이 평생 유효한가요?", "expected_escalate": False, "expected_keyword": "유효기간", "category": "환각"},
    {"question": "무신사 앱 다운로드 링크 알려줘", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "배송비가 무료 아닌가요?", "expected_escalate": False, "expected_keyword": "배송", "category": "환각"},
    {"question": "무신사에서 식품 팔아요?", "expected_escalate": True, "expected_keyword": None, "category": "환각"},
    {"question": "쿠폰 유효기간이 1년 맞죠?", "expected_escalate": False, "expected_keyword": "쿠폰", "category": "환각"},

    # 에스컬레이션 (20개)
    {"question": "화가 많이 났어요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "사기 당한 것 같아요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "책임자 나오세요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "법적 조치 취할게요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "환불 안 해주면 신고할게요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "너무 불만이에요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "상담원 연결해주세요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "이거 완전 사기 아닌가요?", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "심각한 문제가 발생했어요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "소비자보호원에 신고할게요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "너무 화나서 못 참겠어요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "담당자 바꿔주세요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "이런 서비스 처음 봐요 최악이에요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "환불 못 받으면 고소할게요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "본사에 직접 연락할게요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "SNS에 올릴게요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "피해 보상 요구합니다", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "왜 이렇게 서비스가 엉망이에요?", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "관리자 불러주세요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
    {"question": "너무 억울해요", "expected_escalate": True, "expected_keyword": None, "category": "에스컬레이션"},
]

if __name__ == "__main__":
    agent = create_agent()
    results = []
    scores = []

    for case in test_cases:
        print(f"\n질문: {case['question']}")
        result = agent.invoke(
            {
                "user_input": case["question"],
                "category": "",
                "search_results": [],
                "answer": "",
                "escalate": False,
                "retry": False,
                "retry_count": 0
            },
            config={"callbacks": [langfuse_handler]}
        )

        answer = result["answer"]
        escalate = result["escalate"]

        escalate_correct = escalate == case["expected_escalate"]
        keyword_correct = True
        if case["expected_keyword"]:
            keyword_correct = case["expected_keyword"] in answer
        no_hallucination = not any(word in answer for word in ["100일", "아이폰", "주가", "날씨", "로또"])

        score = (escalate_correct + keyword_correct + no_hallucination) / 3
        scores.append(score)

        results.append({
            "category": case["category"],
            "question": case["question"],
            "answer": answer[:200],
            "expected_escalate": case["expected_escalate"],
            "actual_escalate": escalate,
            "escalate_correct": escalate_correct,
            "keyword_correct": keyword_correct,
            "no_hallucination": no_hallucination,
            "score": round(score, 3)
        })

        print(f"점수: {score:.2f}")

    # CSV 저장
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(BASE_DIR, "data", "evaluation_results.csv")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    avg_score = sum(scores) / len(scores)
    print(f"\n✅ 평균 정확도: {avg_score:.3f}")
    print(f"✅ 테스트 케이스: {len(test_cases)}개")
    print(f"✅ CSV 저장 완료: {csv_path}")