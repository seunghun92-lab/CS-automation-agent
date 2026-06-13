import json
from playwright.sync_api import sync_playwright

def crawl_musinsa_faq():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        page.goto("https://store.musinsa.com/app/cs/faq")
        page.wait_for_timeout(3000)
        
        tabs = page.query_selector_all("span[data-mds='TabTextItem']")
        
        faq_data = []
        seen_questions = set()  # 중복 제거용
        
        for tab in tabs:
            tab_name = tab.inner_text()
            print(f"\n=== {tab_name} 탭 크롤링 ===")
            
            tab.click()
            page.wait_for_timeout(2000)
            
            items = page.query_selector_all("span.FaqItem__Title-sc-17ft819-2")
            
            for item in items:
                question = item.inner_text()
                
                # 중복 질문 스킵
                if question in seen_questions:
                    continue
                seen_questions.add(question)
                
                # 클릭해서 답변 펼치기
                item.click()
                page.wait_for_timeout(1000)
                
                # 현재 보이는 답변 가져오기
                answer_el = page.query_selector("div.p-4:visible")
                answer = answer_el.inner_text() if answer_el else "답변 없음"
                
                faq_data.append({
                    "category": tab_name,
                    "question": question,
                    "answer": answer
                })
                print(f"Q: {question}")
                print(f"A: {answer[:50]}...")
        
        browser.close()
        
        with open("../data/musinsa_faq.json", "w", encoding="utf-8") as f:
            json.dump(faq_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n총 {len(faq_data)}개 FAQ 저장 완료!")
        return faq_data

if __name__ == "__main__":
    crawl_musinsa_faq()