import { useState, useRef, useEffect } from "react";

const QUICK_ACTIONS = [
  { label: "내 주문 확인", icon: "📦", prompt: "제 주문을 확인하고 싶어요" },
  { label: "배송 어디까지?", icon: "🚚", prompt: "배송이 어디까지 왔는지 확인하고 싶어요" },
  { label: "교환·반품 신청", icon: "🔄", prompt: "교환 또는 반품하고 싶어요" },
  { label: "궁금한 게 있어요", icon: "💬", prompt: "자주 묻는 질문 알려주세요" },
];

const SAMPLE_HISTORY = [
  { id: 1, title: "주문 O00000001 확인", preview: "상품 준비중입니다", time: "어제" },
  { id: 2, title: "환불 문의", preview: "7일 이내 반품 가능합니다", time: "2일 전" },
  { id: 3, title: "Nimbus 상품 검색", preview: "5개 상품이 검색됩니다", time: "5일 전" },
];

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      content: "안녕하세요! Vella 쇼핑몰 AI 상담사입니다 😊\n주문, 배송, 교환·반품 등 무엇이든 편하게 물어보세요!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    const userText = text || input;
    if (!userText.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: userText }]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userText }),
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { role: "bot", content: data.answer }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "연결에 실패했습니다. 잠시 후 다시 시도해주세요." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.layout}>
      {/* 사이드바 */}
      <aside style={styles.sidebar}>
        <div style={styles.logo}>
          <div style={styles.logoIcon}>V</div>
          <div>
            <div style={styles.logoTitle}>VELLA</div>
            <div style={styles.logoSub}>AI 고객상담</div>
          </div>
        </div>

        <button
          style={styles.newChat}
          onClick={() =>
            setMessages([{
              role: "bot",
              content: "안녕하세요! Vella 쇼핑몰 AI 상담사입니다 😊\n주문, 배송, 교환·반품 등 무엇이든 편하게 물어보세요!",
            }])
          }
        >
          + 새 대화 시작
        </button>

        <div style={styles.sectionLabel}>빠른 도움</div>
        <div style={styles.quickGrid}>
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.label}
              style={styles.quickBtn}
              onClick={() => sendMessage(action.prompt)}
            >
              <span style={styles.quickIcon}>{action.icon}</span>
              <span style={styles.quickLabel}>{action.label}</span>
            </button>
          ))}
        </div>

        <div style={styles.sectionLabel}>최근 대화</div>
        <div style={styles.historyList}>
          {SAMPLE_HISTORY.map((item) => (
            <div key={item.id} style={styles.historyItem}>
              <div style={styles.historyTitle}>{item.title}</div>
              <div style={styles.historyMeta}>
                <span style={styles.historyPreview}>{item.preview}</span>
                <span style={styles.historyTime}>{item.time}</span>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* 메인 채팅 영역 */}
      <main style={styles.main}>
        {/* 헤더 */}
        <div style={styles.header}>
          <div style={styles.agentInfo}>
            <div style={styles.agentAvatar}>AI</div>
            <div>
              <div style={styles.agentName}>Vella 상담사</div>
              <div style={styles.agentStatus}>
                <span style={styles.statusDot}></span>
                24시간 상담 가능
              </div>
            </div>
          </div>
        </div>

        {/* 메시지 영역 */}
        <div style={styles.messages}>
          {messages.map((msg, i) => (
            <div
              key={i}
              style={{
                ...styles.messageRow,
                justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              {msg.role === "bot" && <div style={styles.botAvatar}>AI</div>}
              <div
                style={{
                  ...styles.bubble,
                  ...(msg.role === "user" ? styles.userBubble : styles.botBubble),
                }}
              >
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div style={{ ...styles.messageRow, justifyContent: "flex-start" }}>
              <div style={styles.botAvatar}>AI</div>
              <div style={{ ...styles.bubble, ...styles.botBubble, color: "#999" }}>
                답변을 준비하고 있어요...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 빠른 질문 칩 */}
        <div style={styles.chips}>
          {["주문 O00000001 확인해줘", "환불하고 싶어요", "Nimbus 상품 찾아줘"].map((chip) => (
            <button key={chip} style={styles.chip} onClick={() => sendMessage(chip)}>
               {chip}
            </button>
          ))}
        </div>

        {/* 입력창 */}
        <div style={styles.inputArea}>
          <input
            style={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            placeholder="궁금한 점을 입력해보세요. Enter로 전송"
          />
          <button style={styles.sendBtn} onClick={() => sendMessage()}>
            ▶
          </button>
        </div>
        <div style={styles.footer}>Vella AI 상담사가 도와드립니다.</div>
      </main>
    </div>
  );
}

const styles = {
  layout: { display: "flex", height: "100vh", fontFamily: "'Pretendard', 'Apple SD Gothic Neo', sans-serif", background: "#fff" },
  sidebar: { width: 280, borderRight: "1px solid #f0f0f0", padding: "24px 16px", display: "flex", flexDirection: "column", gap: 8, overflowY: "auto" },
  logo: { display: "flex", alignItems: "center", gap: 12, marginBottom: 16 },
  logoIcon: { width: 40, height: 40, background: "#000", color: "#fff", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 18 },
  logoTitle: { fontWeight: 700, fontSize: 15, letterSpacing: 1 },
  logoSub: { fontSize: 11, color: "#999" },
  newChat: { background: "#000", color: "#fff", border: "none", borderRadius: 10, padding: "12px 16px", cursor: "pointer", fontWeight: 600, fontSize: 14, marginBottom: 8 },
  sectionLabel: { fontSize: 11, color: "#999", fontWeight: 600, marginTop: 16, marginBottom: 8, letterSpacing: 0.5 },
  quickGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 },
  quickBtn: { background: "#f8f8f8", border: "none", borderRadius: 10, padding: "14px 8px", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", gap: 6, transition: "background 0.2s" },
  quickIcon: { fontSize: 22 },
  quickLabel: { fontSize: 11, fontWeight: 600, color: "#333", textAlign: "center" },
  historyList: { display: "flex", flexDirection: "column", gap: 4 },
  historyItem: { padding: "10px 12px", borderRadius: 8, cursor: "pointer", background: "#f8f8f8" },
  historyTitle: { fontSize: 13, fontWeight: 600, color: "#222", marginBottom: 4 },
  historyMeta: { display: "flex", justifyContent: "space-between" },
  historyPreview: { fontSize: 11, color: "#999", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 130 },
  historyTime: { fontSize: 11, color: "#bbb" },
  main: { flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", background: "#FAF8F5" },
  header: { padding: "16px 24px", borderBottom: "1px solid #f0f0f0", display: "flex", alignItems: "center" },
  agentInfo: { display: "flex", alignItems: "center", gap: 12 },
  agentAvatar: { width: 40, height: 40, background: "#000", color: "#fff", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 13 },
  agentName: { fontWeight: 700, fontSize: 15 },
  agentStatus: { display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#666" },
  statusDot: { width: 8, height: 8, background: "#22c55e", borderRadius: "50%", display: "inline-block" },
  messages: { flex: 1, overflowY: "auto", padding: "24px", display: "flex", flexDirection: "column", gap: 16, background: "#FAF8F5" },
  messageRow: { display: "flex", alignItems: "flex-end", gap: 10 },
  botAvatar: { width: 32, height: 32, background: "#000", color: "#fff", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700, flexShrink: 0 },
  bubble: { maxWidth: "65%", padding: "12px 16px", borderRadius: 16, fontSize: 14, lineHeight: 1.6, whiteSpace: "pre-wrap" },
  botBubble: { background: "#ffffff", color: "#222", borderBottomLeftRadius: 4 },
  userBubble: { background: "#000", color: "#fff", borderBottomRightRadius: 4 },
  chips: { display: "flex", gap: 8, padding: "0 24px 12px", flexWrap: "wrap" },
  chip: { background: "#f0f0f0", border: "none", borderRadius: 20, padding: "8px 14px", fontSize: 12, cursor: "pointer", color: "#333", fontWeight: 500 },
  inputArea: { display: "flex", gap: 10, padding: "12px 24px", borderTop: "1px solid #f0f0f0", alignItems: "center" },
  input: { flex: 1, padding: "14px 18px", border: "1px solid #e8e8e8", borderRadius: 12, fontSize: 14, outline: "none", background: "#fafafa" },
  sendBtn: { width: 44, height: 44, background: "#000", color: "#fff", border: "none", borderRadius: 12, cursor: "pointer", fontSize: 16 },
  footer: { textAlign: "center", fontSize: 11, color: "#bbb", padding: "8px 24px 16px" },
};
